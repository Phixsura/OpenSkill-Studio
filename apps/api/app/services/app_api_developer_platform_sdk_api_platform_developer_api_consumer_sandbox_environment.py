"""API Consumer Sandbox Environment — isolated sandbox environments for testing."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class SandboxStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    EXPIRED = "expired"
    DELETED = "deleted"

@dataclass
class SandboxEnv:
    sandbox_id: str
    consumer_id: str
    status: SandboxStatus = SandboxStatus.ACTIVE
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    request_count: int = 0
    request_limit: int = 10000
    data_seeded: bool = False
    reset_count: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSandboxEnvironment:
    def __init__(self, default_ttl_hours: int = 24) -> None:
        self._sandboxes: dict[tuple[str, str], SandboxEnv] = {}
        self._default_ttl = max(1, default_ttl_hours) * 3600

    def create(self, installation_id: str, consumer_id: str, sandbox_id: str, request_limit: int = 10000) -> SandboxEnv:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, sandbox_id)
        if key in self._sandboxes: raise ValueError(f"Sandbox {sandbox_id} already exists")
        if request_limit < 100: raise ValueError("request_limit must be >= 100")
        now = time.time()
        env = SandboxEnv(sandbox_id=sandbox_id, consumer_id=consumer_id, expires_at=now + self._default_ttl, request_limit=request_limit)
        self._sandboxes[key] = env
        return env

    def use_request(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        env = self._get(installation_id, sandbox_id)
        if env.status != SandboxStatus.ACTIVE: raise ValueError(f"Sandbox is {env.status.value}")
        if env.request_count >= env.request_limit: raise ValueError("Request limit reached")
        env.request_count += 1
        return env

    def reset(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        env = self._get(installation_id, sandbox_id)
        env.request_count = 0
        env.data_seeded = False
        env.reset_count += 1
        env.status = SandboxStatus.ACTIVE
        return env

    def pause(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        env = self._get(installation_id, sandbox_id)
        env.status = SandboxStatus.PAUSED
        return env

    def seed_data(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        env = self._get(installation_id, sandbox_id)
        env.data_seeded = True
        return env

    def list_sandboxes(self, installation_id: str, consumer_id: str | None = None) -> list[SandboxEnv]:
        envs = [e for (inst, _), e in self._sandboxes.items() if inst == installation_id]
        if consumer_id: envs = [e for e in envs if e.consumer_id == consumer_id]
        return envs

    def _get(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        env = self._sandboxes.get((installation_id, sandbox_id))
        if env is None: raise KeyError(f"Sandbox {sandbox_id} not found")
        return env
