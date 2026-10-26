"""Runtime Environment — manage isolated runtime environments for extensions.

Provides container-like isolation with resource limits, environment variables,
mounted volumes, and lifecycle management (create/start/stop/destroy).
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class EnvState(str, Enum):
    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    DESTROYED = "destroyed"
    ERROR = "error"


@dataclass
class ResourceLimits:
    cpu_cores: float = 0.5
    memory_mb: int = 256
    disk_mb: int = 512
    max_processes: int = 10
    network_enabled: bool = False


@dataclass
class RuntimeEnvironment:
    env_id: str
    extension_id: str
    runtime: str  # e.g. "node18", "python3.11", "deno"
    state: EnvState = EnvState.CREATED
    limits: ResourceLimits = field(default_factory=ResourceLimits)
    env_vars: dict[str, str] = field(default_factory=dict)
    volumes: list[str] = field(default_factory=list)
    entrypoint: str = ""
    uptime_seconds: int = 0
    created_at: str = ""
    started_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


SUPPORTED_RUNTIMES = {"node18", "node20", "python3.11", "python3.12", "deno", "bun"}
FORBIDDEN_ENV_PREFIXES = ("AWS_", "AZURE_", "GCP_", "SECRET_", "INTERNAL_")


class RuntimeEnvService:
    """Manages sandboxed runtime environments for extensions."""

    def __init__(self):
        self._envs: dict[str, RuntimeEnvironment] = {}

    def create(self, extension_id: str, runtime: str,
               limits: dict | None = None,
               env_vars: dict[str, str] | None = None,
               entrypoint: str = "index.js") -> RuntimeEnvironment:
        if runtime not in SUPPORTED_RUNTIMES:
            raise ValueError(f"Unsupported runtime: {runtime}. Supported: {sorted(SUPPORTED_RUNTIMES)}")

        # Validate env vars
        safe_vars = {}
        for k, v in (env_vars or {}).items():
            if any(k.upper().startswith(p) for p in FORBIDDEN_ENV_PREFIXES):
                raise ValueError(f"Forbidden env var prefix: {k}")
            safe_vars[k] = v

        rl = ResourceLimits()
        if limits:
            if "cpu_cores" in limits:
                rl.cpu_cores = min(max(limits["cpu_cores"], 0.1), 4.0)
            if "memory_mb" in limits:
                rl.memory_mb = min(max(limits["memory_mb"], 64), 2048)
            if "disk_mb" in limits:
                rl.disk_mb = min(max(limits["disk_mb"], 32), 4096)
            if "network_enabled" in limits:
                rl.network_enabled = bool(limits["network_enabled"])

        env_id = f"env_{secrets.token_urlsafe(12)}"
        env = RuntimeEnvironment(
            env_id=env_id, extension_id=extension_id,
            runtime=runtime, limits=rl, env_vars=safe_vars,
            entrypoint=entrypoint,
        )
        self._envs[env_id] = env
        return env

    def start(self, env_id: str) -> dict:
        env = self._envs.get(env_id)
        if not env:
            return {"ok": False, "error": "Environment not found"}
        if env.state not in (EnvState.CREATED, EnvState.STOPPED):
            return {"ok": False, "error": f"Cannot start from state {env.state.value}"}
        env.state = EnvState.RUNNING
        env.started_at = datetime.now(timezone.utc).isoformat()
        return {"ok": True, "env_id": env_id, "state": "running"}

    def stop(self, env_id: str) -> dict:
        env = self._envs.get(env_id)
        if not env:
            return {"ok": False, "error": "Environment not found"}
        if env.state != EnvState.RUNNING:
            return {"ok": False, "error": "Not running"}
        env.state = EnvState.STOPPED
        return {"ok": True, "env_id": env_id, "state": "stopped"}

    def destroy(self, env_id: str) -> bool:
        env = self._envs.get(env_id)
        if not env:
            return False
        if env.state == EnvState.RUNNING:
            env.state = EnvState.STOPPED
        env.state = EnvState.DESTROYED
        return True

    def get_status(self, env_id: str) -> dict | None:
        env = self._envs.get(env_id)
        if not env:
            return None
        return {
            "env_id": env.env_id, "extension_id": env.extension_id,
            "runtime": env.runtime, "state": env.state.value,
            "limits": {"cpu": env.limits.cpu_cores, "memory_mb": env.limits.memory_mb},
            "entrypoint": env.entrypoint,
        }

    def list_envs(self, extension_id: str) -> list[RuntimeEnvironment]:
        return [e for e in self._envs.values()
                if e.extension_id == extension_id and e.state != EnvState.DESTROYED]
