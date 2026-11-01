"""Consumer API Status Page — aggregate service status for consumer-facing display."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class ServiceComponent:
    component_id: str
    name: str
    status: str = "operational"  # "operational", "degraded", "partial_outage", "major_outage"
    description: str = ""
    updated_at: datetime | None = None

@dataclass
class StatusSummary:
    overall_status: str
    components: list[ServiceComponent]
    active_incidents: int
    uptime_pct_30d: float

STATUS_PRIORITY = {"major_outage": 0, "partial_outage": 1, "degraded": 2, "operational": 3}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiStatusPage:
    def __init__(self) -> None:
        self._components: dict[tuple[str, str], ServiceComponent] = {}

    def add_component(self, installation_id: str, component: ServiceComponent) -> ServiceComponent:
        if not installation_id:
            raise ValueError("installation_id is required")
        if component.status not in STATUS_PRIORITY:
            raise ValueError(f"Invalid status: {component.status}")
        component.updated_at = component.updated_at or datetime.utcnow()
        self._components[(installation_id, component.component_id)] = component
        return component

    def update_status(self, installation_id: str, component_id: str, status: str) -> ServiceComponent:
        key = (installation_id, component_id)
        comp = self._components.get(key)
        if not comp:
            raise ValueError("Component not found")
        if status not in STATUS_PRIORITY:
            raise ValueError(f"Invalid status: {status}")
        comp.status = status
        comp.updated_at = datetime.utcnow()
        log.info("component_status_updated", installation_id=installation_id, component=comp.name, status=status)
        return comp

    def get_summary(self, installation_id: str, active_incidents: int = 0, uptime_30d: float = 99.9) -> StatusSummary:
        components = sorted(
            [c for (inst, _), c in self._components.items() if inst == installation_id],
            key=lambda c: STATUS_PRIORITY.get(c.status, 3),
        )
        if not components:
            overall = "operational"
        else:
            worst = min(STATUS_PRIORITY.get(c.status, 3) for c in components)
            overall = {0: "major_outage", 1: "partial_outage", 2: "degraded", 3: "operational"}[worst]
        return StatusSummary(overall_status=overall, components=components, active_incidents=active_incidents, uptime_pct_30d=uptime_30d)

    def list_components(self, installation_id: str) -> list[ServiceComponent]:
        return [c for (inst, _), c in self._components.items() if inst == installation_id]
