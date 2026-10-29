"""App API Developer System Status — overall system health and component status."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ComponentStatus:
    name: str
    status: str  # "operational", "degraded", "outage", "maintenance"

@dataclass
class SystemStatus:
    components: list[ComponentStatus] = field(default_factory=list)
    active_incidents: int = 0
    scheduled_maintenance: int = 0

    @property
    def overall(self) -> str:
        if any(c.status == "outage" for c in self.components): return "major_outage"
        if any(c.status == "degraded" for c in self.components): return "partial_degradation"
        if any(c.status == "maintenance" for c in self.components): return "maintenance"
        return "all_systems_operational"

class AppAPIDeveloperAPISystemStatus:
    def __init__(self) -> None:
        self._statuses: dict[str, SystemStatus] = {}

    def set_status(self, installation_id: str, components: list[dict], active_incidents: int = 0, scheduled_maintenance: int = 0) -> SystemStatus:
        if not installation_id: raise ValueError("installation_id is required")
        comps = [ComponentStatus(name=c["name"], status=c["status"]) for c in components]
        s = SystemStatus(components=comps, active_incidents=active_incidents, scheduled_maintenance=scheduled_maintenance)
        self._statuses[installation_id] = s
        return s

    def get(self, installation_id: str) -> SystemStatus:
        return self._statuses.get(installation_id, SystemStatus())
