"""App API Developer API Service Registry — register and discover API services."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RegisteredService:
    service_id: str
    name: str
    base_url: str
    version: str
    health_check_url: str = ""
    tags: list[str] = field(default_factory=list)
    registered_at: float = field(default_factory=time.time)
    last_heartbeat_at: float = field(default_factory=time.time)
    status: str = "active"

    @property
    def stale(self) -> bool:
        return time.time() - self.last_heartbeat_at > 300  # 5 min without heartbeat

class AppAPIDeveloperAPIApiDeveloperApiApiServiceRegistry:
    def __init__(self) -> None:
        self._services: dict[tuple[str, str], RegisteredService] = {}

    def register(self, installation_id: str, service_id: str, name: str, base_url: str, version: str, health_check_url: str = "", tags: list[str] | None = None) -> RegisteredService:
        if not installation_id: raise ValueError("installation_id is required")
        if not base_url.startswith("https://"): raise ValueError("base_url must use HTTPS")
        key = (installation_id, service_id)
        s = RegisteredService(service_id=service_id, name=name, base_url=base_url, version=version, health_check_url=health_check_url, tags=tags or [])
        self._services[key] = s
        return s

    def heartbeat(self, installation_id: str, service_id: str) -> RegisteredService:
        s = self._get(installation_id, service_id)
        s.last_heartbeat_at = time.time()
        return s

    def deregister(self, installation_id: str, service_id: str) -> None:
        key = (installation_id, service_id)
        s = self._services.get(key)
        if s: s.status = "inactive"

    def discover(self, installation_id: str, tag: str | None = None, version: str | None = None) -> list[RegisteredService]:
        services = [s for (inst, _), s in self._services.items() if inst == installation_id and s.status == "active"]
        if tag: services = [s for s in services if tag in s.tags]
        if version: services = [s for s in services if s.version == version]
        return services

    def stale_services(self, installation_id: str) -> list[RegisteredService]:
        return [s for (inst, _), s in self._services.items() if inst == installation_id and s.stale and s.status == "active"]

    def all_services(self, installation_id: str) -> list[RegisteredService]:
        return [s for (inst, _), s in self._services.items() if inst == installation_id]

    def _get(self, installation_id: str, service_id: str) -> RegisteredService:
        key = (installation_id, service_id)
        s = self._services.get(key)
        if s is None: raise KeyError(f"Service {service_id} not found")
        return s
