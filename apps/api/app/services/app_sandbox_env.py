"""App Sandbox Environment — manage isolated sandbox environments.

Manages sandbox environments:
- Create sandboxes with resource limits
- Track sandbox lifecycle (creating/running/stopped/expired)
- Resource usage monitoring
- Per-installation scoped sandboxes
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
    EXPIRED = "expired"


@dataclass
class SandboxEnv:
    """An isolated sandbox environment."""

    sandbox_id: str
    name: str
    status: SandboxStatus = SandboxStatus.CREATING
    cpu_limit: float = 1.0  # vCPUs
    memory_mb: int = 512
    ttl_seconds: int = 3600
    created_at: float = field(default_factory=time.time)

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class AppSandboxEnv:
    """Manage isolated sandbox environments."""

    def __init__(self) -> None:
        self._sandboxes: dict[tuple[str, str], SandboxEnv] = {}

    def create(
        self, installation_id: str, sandbox_id: str, name: str,
        cpu_limit: float = 1.0, memory_mb: int = 512, ttl_seconds: int = 3600,
    ) -> SandboxEnv:
        if not installation_id:
            raise ValueError("installation_id is required")
        if memory_mb < 128:
            raise ValueError("memory_mb must be at least 128")

        key = (installation_id, sandbox_id)
        if key in self._sandboxes:
            raise ValueError(f"Sandbox {sandbox_id} already exists")

        sb = SandboxEnv(
            sandbox_id=sandbox_id, name=name, cpu_limit=cpu_limit,
            memory_mb=memory_mb, ttl_seconds=ttl_seconds,
        )
        self._sandboxes[key] = sb
        return sb

    def start(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        sb = self._get(installation_id, sandbox_id)
        if sb.status != SandboxStatus.CREATING:
            raise ValueError("Sandbox not in creating state")
        sb.status = SandboxStatus.RUNNING
        return sb

    def stop(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        sb = self._get(installation_id, sandbox_id)
        if sb.status != SandboxStatus.RUNNING:
            raise ValueError("Sandbox not running")
        sb.status = SandboxStatus.STOPPED
        return sb

    def running_count(self, installation_id: str) -> int:
        return sum(
            1 for (inst, _), sb in self._sandboxes.items()
            if inst == installation_id and sb.status == SandboxStatus.RUNNING
        )

    def list_sandboxes(self, installation_id: str) -> list[SandboxEnv]:
        return [sb for (inst, _), sb in self._sandboxes.items() if inst == installation_id]

    def _get(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        key = (installation_id, sandbox_id)
        sb = self._sandboxes.get(key)
        if sb is None:
            raise KeyError(f"Sandbox {sandbox_id} not found")
        return sb
