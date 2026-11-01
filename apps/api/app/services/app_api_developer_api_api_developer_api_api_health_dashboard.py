"""App API Developer API Health Dashboard — real-time multi-service health view."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ServiceHealth:
    service_name: str
    status: str = "healthy"  # "healthy", "degraded", "unhealthy", "unknown"
    response_time_ms: float = 0.0
    last_check_at: float = field(default_factory=time.time)
    error_message: str = ""
    consecutive_failures: int = 0

class AppAPIDeveloperAPIApiDeveloperApiApiHealthDashboard:
    def __init__(self) -> None:
        self._services: dict[tuple[str, str], ServiceHealth] = {}

    def register_service(self, installation_id: str, service_name: str) -> ServiceHealth:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, service_name)
        s = ServiceHealth(service_name=service_name)
        self._services[key] = s
        return s

    def update_health(self, installation_id: str, service_name: str, status: str, response_time_ms: float = 0.0, error_message: str = "") -> ServiceHealth:
        if status not in ("healthy", "degraded", "unhealthy", "unknown"): raise ValueError("invalid status")
        key = (installation_id, service_name)
        s = self._services.get(key)
        if s is None: raise KeyError(f"Service {service_name} not found")
        s.status = status
        s.response_time_ms = response_time_ms
        s.last_check_at = time.time()
        s.error_message = error_message
        if status in ("unhealthy", "degraded"):
            s.consecutive_failures += 1
        else:
            s.consecutive_failures = 0
        return s

    def overall_status(self, installation_id: str) -> str:
        services = self.all_services(installation_id)
        if not services: return "unknown"
        if any(s.status == "unhealthy" for s in services): return "unhealthy"
        if any(s.status == "degraded" for s in services): return "degraded"
        if all(s.status == "healthy" for s in services): return "healthy"
        return "unknown"

    def all_services(self, installation_id: str) -> list[ServiceHealth]:
        return [s for (inst, _), s in self._services.items() if inst == installation_id]

    def unhealthy_services(self, installation_id: str) -> list[ServiceHealth]:
        return [s for s in self.all_services(installation_id) if s.status in ("unhealthy", "degraded")]
