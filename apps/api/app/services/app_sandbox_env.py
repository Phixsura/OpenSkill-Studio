"""App Sandbox Environment — manage isolated sandbox environments for app testing.

Provides sandbox lifecycle management:
- Create sandboxes with resource limits (memory, CPU, timeout)
- Track sandbox status: creating → running → stopped → terminated
- Execution log capture
- Per-installation scoped sandboxes
- Resource usage tracking
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class SandboxStatus(str, Enum):
    CREATING = "creating"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"
    ERROR = "error"


@dataclass
class ResourceLimits:
    """Resource limits for a sandbox."""

    memory_mb: int = 256
    cpu_cores: float = 0.5
    timeout_seconds: int = 300
    max_storage_mb: int = 512


@dataclass
class SandboxInstance:
    """A sandbox environment instance."""

    sandbox_id: str
    installation_id: str
    app_version: str
    status: SandboxStatus = SandboxStatus.CREATING
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    stopped_at: float | None = None
    exit_code: int | None = None
    logs: list[str] = field(default_factory=list)
    memory_used_mb: float = 0.0
    cpu_used_seconds: float = 0.0


class AppSandboxManager:
    """Manage isolated sandbox environments for app testing."""

    def __init__(self, max_per_installation: int = 5) -> None:
        self._sandboxes: dict[tuple[str, str], SandboxInstance] = {}
        self._max_per_installation = max_per_installation

    def create_sandbox(
        self,
        installation_id: str,
        sandbox_id: str,
        app_version: str,
        limits: ResourceLimits | None = None,
    ) -> SandboxInstance:
        """Create a new sandbox environment."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not sandbox_id:
            raise ValueError("sandbox_id is required")
        if not app_version:
            raise ValueError("app_version is required")

        key = (installation_id, sandbox_id)
        if key in self._sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} already exists")

        # Check per-installation limit
        active = self._count_active(installation_id)
        if active >= self._max_per_installation:
            raise ValueError(
                f"Maximum {self._max_per_installation} active sandboxes per installation"
            )

        sandbox = SandboxInstance(
            sandbox_id=sandbox_id,
            installation_id=installation_id,
            app_version=app_version,
            limits=limits or ResourceLimits(),
        )
        self._sandboxes[key] = sandbox
        log.info("sandbox.created", sandbox_id=sandbox_id, app_version=app_version)
        return sandbox

    def start_sandbox(self, installation_id: str, sandbox_id: str) -> SandboxInstance:
        """Start a sandbox."""
        sb = self._get(installation_id, sandbox_id)
        if sb.status != SandboxStatus.CREATING:
            raise ValueError(f"Cannot start sandbox in {sb.status} state")
        sb.status = SandboxStatus.RUNNING
        sb.started_at = time.time()
        return sb

    def stop_sandbox(
        self, installation_id: str, sandbox_id: str, exit_code: int = 0
    ) -> SandboxInstance:
        """Stop a running sandbox."""
        sb = self._get(installation_id, sandbox_id)
        if sb.status != SandboxStatus.RUNNING:
            raise ValueError(f"Cannot stop sandbox in {sb.status} state")
        sb.status = SandboxStatus.STOPPED
        sb.stopped_at = time.time()
        sb.exit_code = exit_code
        return sb

    def terminate_sandbox(self, installation_id: str, sandbox_id: str) -> SandboxInstance:
        """Force terminate a sandbox."""
        sb = self._get(installation_id, sandbox_id)
        if sb.status in (SandboxStatus.TERMINATED,):
            raise ValueError("Sandbox already terminated")
        sb.status = SandboxStatus.TERMINATED
        sb.stopped_at = sb.stopped_at or time.time()
        return sb

    def append_log(self, installation_id: str, sandbox_id: str, line: str) -> None:
        """Append a log line to the sandbox."""
        sb = self._get(installation_id, sandbox_id)
        sb.logs.append(line)

    def update_usage(
        self, installation_id: str, sandbox_id: str,
        memory_mb: float = 0.0, cpu_seconds: float = 0.0,
    ) -> SandboxInstance:
        """Update resource usage metrics."""
        sb = self._get(installation_id, sandbox_id)
        sb.memory_used_mb = max(0.0, memory_mb)
        sb.cpu_used_seconds = max(0.0, cpu_seconds)
        return sb

    def get_sandbox(self, installation_id: str, sandbox_id: str) -> SandboxInstance:
        return self._get(installation_id, sandbox_id)

    def list_sandboxes(self, installation_id: str) -> list[SandboxInstance]:
        return [
            sb for (inst, _), sb in self._sandboxes.items()
            if inst == installation_id
        ]

    def get_logs(self, installation_id: str, sandbox_id: str, tail: int = 0) -> list[str]:
        sb = self._get(installation_id, sandbox_id)
        if tail > 0:
            return sb.logs[-tail:]
        return list(sb.logs)

    def _count_active(self, installation_id: str) -> int:
        return sum(
            1 for (inst, _), sb in self._sandboxes.items()
            if inst == installation_id
            and sb.status in (SandboxStatus.CREATING, SandboxStatus.RUNNING)
        )

    def _get(self, installation_id: str, sandbox_id: str) -> SandboxInstance:
        key = (installation_id, sandbox_id)
        sb = self._sandboxes.get(key)
        if sb is None:
            raise KeyError(f"Sandbox {sandbox_id} not found")
        return sb
