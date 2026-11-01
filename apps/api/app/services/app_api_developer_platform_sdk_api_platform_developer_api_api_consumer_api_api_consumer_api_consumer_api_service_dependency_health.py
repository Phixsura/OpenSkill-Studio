"""Consumer API Service Dependency Health — monitor health of upstream service dependencies."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ServiceDependency:
    service_id: str
    name: str
    endpoint: str
    criticality: str = "required"  # "required", "optional", "degraded"
    status: str = "healthy"  # "healthy", "degraded", "down", "unknown"
    last_checked_at: datetime | None = None
    response_time_ms: float = 0.0

@dataclass
class DependencyHealthReport:
    overall_status: str
    healthy_count: int
    degraded_count: int
    down_count: int
    dependencies: list[ServiceDependency]

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiServiceDependencyHealth:
    def __init__(self) -> None:
        self._deps: dict[tuple[str, str], ServiceDependency] = {}

    def register(self, installation_id: str, dep: ServiceDependency) -> ServiceDependency:
        if not installation_id:
            raise ValueError("installation_id is required")
        if dep.criticality not in ("required", "optional", "degraded"):
            raise ValueError(f"Invalid criticality: {dep.criticality}")
        self._deps[(installation_id, dep.service_id)] = dep
        return dep

    def update_status(self, installation_id: str, service_id: str, status: str, response_time_ms: float = 0, now: datetime | None = None) -> ServiceDependency:
        key = (installation_id, service_id)
        dep = self._deps.get(key)
        if not dep:
            raise ValueError("Dependency not found")
        if status not in ("healthy", "degraded", "down", "unknown"):
            raise ValueError(f"Invalid status: {status}")
        dep.status = status
        dep.response_time_ms = response_time_ms
        dep.last_checked_at = now or datetime.utcnow()
        return dep

    def get_report(self, installation_id: str) -> DependencyHealthReport:
        deps = [d for (inst, _), d in self._deps.items() if inst == installation_id]
        healthy = sum(1 for d in deps if d.status == "healthy")
        degraded = sum(1 for d in deps if d.status == "degraded")
        down = sum(1 for d in deps if d.status == "down")
        # Overall: down if any required is down, degraded if any required is degraded
        required_down = any(d.status == "down" and d.criticality == "required" for d in deps)
        required_degraded = any(d.status == "degraded" and d.criticality == "required" for d in deps)
        if required_down:
            overall = "down"
        elif required_degraded or down > 0:
            overall = "degraded"
        else:
            overall = "healthy"
        return DependencyHealthReport(overall_status=overall, healthy_count=healthy, degraded_count=degraded, down_count=down, dependencies=sorted(deps, key=lambda d: ({"down": 0, "degraded": 1, "unknown": 2, "healthy": 3}.get(d.status, 4))))

    def list_dependencies(self, installation_id: str) -> list[ServiceDependency]:
        return [d for (inst, _), d in self._deps.items() if inst == installation_id]
