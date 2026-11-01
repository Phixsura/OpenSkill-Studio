"""App API Developer API Status Page Manager — public status page configuration."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class StatusComponent:
    component_id: str
    name: str
    status: str = "operational"  # "operational", "degraded", "partial_outage", "major_outage", "maintenance"
    updated_at: float = field(default_factory=time.time)

@dataclass
class StatusIncident:
    incident_id: str
    title: str
    status: str  # "investigating", "identified", "monitoring", "resolved"
    impact: str  # "none", "minor", "major", "critical"
    message: str = ""
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiStatusPageManager:
    def __init__(self) -> None:
        self._components: dict[tuple[str, str], StatusComponent] = {}
        self._incidents: dict[tuple[str, str], StatusIncident] = {}

    def add_component(self, installation_id: str, component_id: str, name: str) -> StatusComponent:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, component_id)
        c = StatusComponent(component_id=component_id, name=name)
        self._components[key] = c
        return c

    def update_component(self, installation_id: str, component_id: str, status: str) -> StatusComponent:
        valid = {"operational", "degraded", "partial_outage", "major_outage", "maintenance"}
        if status not in valid: raise ValueError(f"Invalid status: {status}")
        key = (installation_id, component_id)
        c = self._components.get(key)
        if c is None: raise KeyError(f"Component {component_id} not found")
        c.status = status
        c.updated_at = time.time()
        return c

    def create_incident(self, installation_id: str, incident_id: str, title: str, impact: str, message: str = "") -> StatusIncident:
        if impact not in ("none", "minor", "major", "critical"): raise ValueError("invalid impact")
        key = (installation_id, incident_id)
        i = StatusIncident(incident_id=incident_id, title=title, status="investigating", impact=impact, message=message)
        self._incidents[key] = i
        return i

    def overall_status(self, installation_id: str) -> str:
        comps = [c for (inst, _), c in self._components.items() if inst == installation_id]
        if not comps: return "operational"
        if any(c.status == "major_outage" for c in comps): return "major_outage"
        if any(c.status == "partial_outage" for c in comps): return "partial_outage"
        if any(c.status == "degraded" for c in comps): return "degraded"
        if any(c.status == "maintenance" for c in comps): return "maintenance"
        return "operational"

    def all_components(self, installation_id: str) -> list[StatusComponent]:
        return [c for (inst, _), c in self._components.items() if inst == installation_id]
