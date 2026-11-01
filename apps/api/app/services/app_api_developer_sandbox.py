"""App API Developer Sandbox — isolated testing environments for developers."""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class Sandbox:
    sandbox_id: str
    developer_id: str
    api_key: str
    base_url: str
    created_at: float = field(default_factory=time.time)
    request_count: int = 0
    active: bool = True

class AppAPIDeveloperSandbox:
    def __init__(self) -> None:
        self._sandboxes: dict[tuple[str, str], Sandbox] = {}

    def create(self, installation_id: str, sandbox_id: str, developer_id: str, base_url: str) -> Sandbox:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, sandbox_id)
        if key in self._sandboxes: raise ValueError(f"Sandbox {sandbox_id} already exists")
        api_key = f"sb_{secrets.token_urlsafe(24)}"
        sb = Sandbox(sandbox_id=sandbox_id, developer_id=developer_id, api_key=api_key, base_url=base_url)
        self._sandboxes[key] = sb
        return sb

    def record_request(self, installation_id: str, sandbox_id: str) -> Sandbox:
        sb = self._get(installation_id, sandbox_id)
        sb.request_count += 1
        return sb

    def deactivate(self, installation_id: str, sandbox_id: str) -> Sandbox:
        sb = self._get(installation_id, sandbox_id)
        sb.active = False
        return sb

    def active_sandboxes(self, installation_id: str) -> list[Sandbox]:
        return [sb for (inst, _), sb in self._sandboxes.items() if inst == installation_id and sb.active]

    def list_sandboxes(self, installation_id: str) -> list[Sandbox]:
        return [sb for (inst, _), sb in self._sandboxes.items() if inst == installation_id]

    def _get(self, installation_id: str, sandbox_id: str) -> Sandbox:
        sb = self._sandboxes.get((installation_id, sandbox_id))
        if sb is None: raise KeyError(f"Sandbox {sandbox_id} not found")
        return sb
