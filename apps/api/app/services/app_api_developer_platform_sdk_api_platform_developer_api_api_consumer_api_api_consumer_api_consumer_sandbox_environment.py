"""Consumer Sandbox Environment — isolated testing environments per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class SandboxConfig:
    sandbox_id: str
    consumer_id: str
    name: str
    rate_limit_rps: int = 10
    mock_responses: bool = True
    seed_data: bool = True
    ttl_hours: int = 72
    status: str = "active"  # "active", "expired", "destroyed"
    created_at: datetime | None = None

@dataclass
class SandboxRequest:
    request_id: str
    method: str
    path: str
    timestamp: datetime
    response_status: int
    mocked: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerSandboxEnvironment:
    def __init__(self) -> None:
        self._sandboxes: dict[tuple[str, str], SandboxConfig] = {}
        self._requests: dict[tuple[str, str], list[SandboxRequest]] = {}

    def create(self, installation_id: str, config: SandboxConfig) -> SandboxConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, config.sandbox_id)
        if key in self._sandboxes:
            raise ValueError(f"Sandbox {config.sandbox_id} already exists")
        config.status = "active"
        config.created_at = config.created_at or datetime.utcnow()
        self._sandboxes[key] = config
        log.info("sandbox_created", installation_id=installation_id, sandbox_id=config.sandbox_id)
        return config

    def get(self, installation_id: str, sandbox_id: str) -> SandboxConfig | None:
        return self._sandboxes.get((installation_id, sandbox_id))

    def destroy(self, installation_id: str, sandbox_id: str) -> SandboxConfig:
        key = (installation_id, sandbox_id)
        sb = self._sandboxes.get(key)
        if not sb:
            raise ValueError("Sandbox not found")
        sb.status = "destroyed"
        self._requests.pop(key, None)
        return sb

    def record_request(self, installation_id: str, sandbox_id: str, req: SandboxRequest) -> SandboxRequest:
        key = (installation_id, sandbox_id)
        if key not in self._sandboxes:
            raise ValueError("Sandbox not found")
        if self._sandboxes[key].status != "active":
            raise ValueError("Sandbox is not active")
        if key not in self._requests:
            self._requests[key] = []
        self._requests[key].append(req)
        return req

    def get_requests(self, installation_id: str, sandbox_id: str) -> list[SandboxRequest]:
        return self._requests.get((installation_id, sandbox_id), [])

    def list_sandboxes(self, installation_id: str, consumer_id: str | None = None) -> list[SandboxConfig]:
        return [s for (inst, _), s in self._sandboxes.items() if inst == installation_id and (consumer_id is None or s.consumer_id == consumer_id)]
