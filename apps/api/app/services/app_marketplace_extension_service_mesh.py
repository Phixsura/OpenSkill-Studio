"""Extension Service Mesh — inter-extension communication with circuit breaking."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class ServiceEndpoint:
    service_id: str
    extension_id: str
    url: str
    healthy: bool = True
    request_count: int = 0
    error_count: int = 0
    circuit_open: bool = False
    last_error: float = 0.0


class ExtServiceMeshService:
    ERROR_THRESHOLD = 5  # errors before circuit opens
    RECOVERY_TIME = 30  # seconds before circuit half-opens

    def __init__(self):
        self._services: dict[str, ServiceEndpoint] = {}

    def register(self, service_id: str, extension_id: str, url: str) -> ServiceEndpoint:
        ep = ServiceEndpoint(service_id=service_id, extension_id=extension_id, url=url)
        self._services[service_id] = ep
        return ep

    def call(self, service_id: str) -> tuple[bool, str]:
        ep = self._services.get(service_id)
        if not ep:
            return False, "Service not found"
        if ep.circuit_open:
            if time.time() - ep.last_error > self.RECOVERY_TIME:
                ep.circuit_open = False  # half-open
            else:
                return False, "Circuit breaker open"
        ep.request_count += 1
        return True, ep.url

    def report_success(self, service_id: str) -> None:
        ep = self._services.get(service_id)
        if ep:
            ep.error_count = 0
            ep.circuit_open = False

    def report_error(self, service_id: str) -> None:
        ep = self._services.get(service_id)
        if ep:
            ep.error_count += 1
            ep.last_error = time.time()
            if ep.error_count >= self.ERROR_THRESHOLD:
                ep.circuit_open = True

    def get_topology(self) -> list[ServiceEndpoint]:
        return list(self._services.values())

    def get_health(self) -> dict:
        total = len(self._services)
        healthy = sum(1 for s in self._services.values() if not s.circuit_open)
        return {"total": total, "healthy": healthy, "unhealthy": total - healthy}
