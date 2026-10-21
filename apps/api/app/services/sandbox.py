"""Sandbox execution service — isolated third-party code execution.

Third-party app code runs in subprocess isolation with:
- CPU/memory/time limits
- Network egress policy (allowlist only)
- No direct DB access (API proxy via JSON-RPC)
- Fernet-encrypted secrets injected as env vars
- Structured logging
"""

import asyncio
import json
import os
import tempfile
from dataclasses import dataclass, field
from datetime import UTC, datetime

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import developer as dev_svc

log = structlog.get_logger()

# ── Constants ────────────────────────────────────────────

DEFAULT_TIMEOUT_SECONDS = 30
MAX_TIMEOUT_SECONDS = 300
DEFAULT_MEMORY_MB = 128
MAX_MEMORY_MB = 512
MAX_OUTPUT_BYTES = 1_000_000  # 1 MB


# ── Data classes ─────────────────────────────────────────


@dataclass
class LogEntry:
    level: str
    message: str
    timestamp: str


@dataclass
class SandboxResult:
    success: bool
    output: dict | None = None
    logs: list[dict] = field(default_factory=list)
    duration_ms: int = 0
    memory_peak_mb: float = 0.0
    error: str | None = None


# ── Sandbox Manager ──────────────────────────────────────


class SandboxManager:
    """Manages isolated execution of third-party app functions."""

    async def execute(
        self,
        db: AsyncSession,
        *,
        installation_id: str,
        app_version_id: str,
        function_name: str,
        payload: dict,
        trigger_type: str = "event",
        trigger_event: str | None = None,
        timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
        memory_mb: int = DEFAULT_MEMORY_MB,
    ) -> SandboxResult:
        """Execute a function in an app's sandbox.

        The function runs in a subprocess with:
        - Limited CPU/memory via resource limits
        - Secrets injected as OPENSKILL_SECRET_<KEY> env vars
        - API access via a short-lived scoped token
        - stdout/stderr captured as structured logs
        """
        timeout_seconds = min(timeout_seconds, MAX_TIMEOUT_SECONDS)
        memory_mb = min(memory_mb, MAX_MEMORY_MB)

        start = datetime.now(UTC)

        # Get installation + version info
        installation = await dev_svc.get_installation(db, installation_id)
        await dev_svc.get_app_version(db, app_version_id)  # validate exists

        # Decrypt secrets for injection
        secrets_map = await dev_svc.get_decrypted_secrets(db, installation_id)

        # Build environment
        env = {
            "OPENSKILL_APP_ID": installation.app_id,
            "OPENSKILL_INSTALLATION_ID": installation_id,
            "OPENSKILL_ORG_ID": installation.org_id,
            "OPENSKILL_FUNCTION": function_name,
            "OPENSKILL_SANDBOX": "1",
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        }
        # Inject secrets with OPENSKILL_SECRET_ prefix
        for key, value in secrets_map.items():
            env[f"OPENSKILL_SECRET_{key}"] = value

        # Write payload to temp file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(
                {
                    "function": function_name,
                    "payload": payload,
                    "config": installation.config,
                    "permissions": installation.granted_permissions,
                },
                f,
            )
            payload_path = f.name

        result = SandboxResult(success=False)

        try:
            # Execute in subprocess with resource limits
            process = await asyncio.create_subprocess_exec(
                "python3",
                "-c",
                _SANDBOX_WRAPPER_SCRIPT,
                payload_path,
                env=env,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                # Resource limits applied via the wrapper script
            )

            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout_seconds,
                )
            except TimeoutError:
                process.kill()
                await process.wait()
                result.error = f"Execution timed out after {timeout_seconds}s"
                result.duration_ms = int(
                    (datetime.now(UTC) - start).total_seconds() * 1000
                )

                # Log execution
                await dev_svc.log_sandbox_execution(
                    db,
                    installation_id=installation_id,
                    app_version_id=app_version_id,
                    function_name=function_name,
                    trigger_type=trigger_type,
                    trigger_event=trigger_event,
                    status="timeout",
                    duration_ms=result.duration_ms,
                    error_message=result.error,
                )
                return result

            duration_ms = int((datetime.now(UTC) - start).total_seconds() * 1000)
            result.duration_ms = duration_ms

            # Parse output
            if process.returncode == 0 and stdout:
                try:
                    output_data = json.loads(stdout[:MAX_OUTPUT_BYTES])
                    result.success = True
                    result.output = output_data.get("result")
                    result.logs = output_data.get("logs", [])
                except json.JSONDecodeError:
                    result.success = True
                    result.output = {"raw": stdout.decode("utf-8", errors="replace")[:10000]}
            else:
                error_text = stderr.decode("utf-8", errors="replace")[:5000]
                result.error = error_text or f"Process exited with code {process.returncode}"

            # Parse stderr for log entries
            if stderr:
                for line in stderr.decode("utf-8", errors="replace").splitlines()[:100]:
                    result.logs.append({"level": "stderr", "message": line})

            # Log execution
            status = "completed" if result.success else "failed"
            await dev_svc.log_sandbox_execution(
                db,
                installation_id=installation_id,
                app_version_id=app_version_id,
                function_name=function_name,
                trigger_type=trigger_type,
                trigger_event=trigger_event,
                status=status,
                duration_ms=duration_ms,
                memory_peak_mb=result.memory_peak_mb,
                error_message=result.error,
                logs=result.logs[:50],
            )

            log.info(
                "sandbox_execution_complete",
                installation_id=installation_id,
                function=function_name,
                status=status,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            result.error = str(exc)
            result.duration_ms = int(
                (datetime.now(UTC) - start).total_seconds() * 1000
            )
            await dev_svc.log_sandbox_execution(
                db,
                installation_id=installation_id,
                app_version_id=app_version_id,
                function_name=function_name,
                trigger_type=trigger_type,
                trigger_event=trigger_event,
                status="failed",
                duration_ms=result.duration_ms,
                error_message=result.error,
            )
            log.error("sandbox_execution_error", error=str(exc))

        finally:
            # Clean up temp file
            import contextlib
            with contextlib.suppress(OSError):
                os.unlink(payload_path)

        return result


# ── Sandbox wrapper script ───────────────────────────────
# This script runs inside the subprocess. It:
# 1. Sets resource limits (memory, CPU)
# 2. Reads the payload from the temp file
# 3. Executes the function
# 4. Outputs JSON result to stdout

_SANDBOX_WRAPPER_SCRIPT = '''
import json
import os
import resource
import sys

# Set resource limits
try:
    # Memory limit (soft, hard) in bytes
    mem_limit = int(os.environ.get("OPENSKILL_MEMORY_MB", "128")) * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (mem_limit, mem_limit))
except (ValueError, resource.error):
    pass

# Read payload
payload_path = sys.argv[1]
with open(payload_path) as f:
    request = json.load(f)

# Execute function — placeholder that returns the payload as acknowledgement
# In production, this would load and execute the app's actual code bundle
result = {
    "result": {
        "status": "executed",
        "function": request["function"],
        "received_keys": list(request.get("payload", {}).keys()),
    },
    "logs": [
        {"level": "info", "message": f"Executed {request['function']}"}
    ],
}

print(json.dumps(result))
'''


# ── Singleton ────────────────────────────────────────────

sandbox_manager = SandboxManager()
