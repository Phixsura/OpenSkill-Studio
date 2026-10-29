"""App API Developer API Sandbox Environment — isolated testing environments."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class SandboxEnv:
    sandbox_id: str
    name: str
    base_url: str
    status: str = "active"  # "active", "paused", "expired"
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    request_count: int = 0
    data_isolated: bool = True

    @property
    def expired(self) -> bool:
        return self.expires_at > 0 and time.time() > self.expires_at

class AppAPIDeveloperAPIApiSandboxEnvironment:
    def __init__(self) -> None:
        self._sandboxes: dict[tuple[str, str], SandboxEnv] = {}

    def create(self, installation_id: str, sandbox_id: str, name: str, base_url: str, ttl_hours: int = 24) -> SandboxEnv:
        if not installation_id: raise ValueError("installation_id is required")
        if not base_url.startswith("https://"): raise ValueError("base_url must use HTTPS")
        key = (installation_id, sandbox_id)
        if key in self._sandboxes: raise ValueError(f"Sandbox {sandbox_id} exists")
        s = SandboxEnv(sandbox_id=sandbox_id, name=name, base_url=base_url, expires_at=time.time() + ttl_hours * 3600)
        self._sandboxes[key] = s
        return s

    def use(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        s = self._get(installation_id, sandbox_id)
        if s.expired:
            s.status = "expired"
            raise ValueError("Sandbox has expired")
        s.request_count += 1
        return s

    def pause(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        s = self._get(installation_id, sandbox_id)
        s.status = "paused"
        return s

    def active_sandboxes(self, installation_id: str) -> list[SandboxEnv]:
        return [s for (inst, _), s in self._sandboxes.items() if inst == installation_id and s.status == "active" and not s.expired]

    def all_sandboxes(self, installation_id: str) -> list[SandboxEnv]:
        return [s for (inst, _), s in self._sandboxes.items() if inst == installation_id]

    def _get(self, installation_id: str, sandbox_id: str) -> SandboxEnv:
        key = (installation_id, sandbox_id)
        s = self._sandboxes.get(key)
        if s is None: raise KeyError(f"Sandbox {sandbox_id} not found")
        return s
