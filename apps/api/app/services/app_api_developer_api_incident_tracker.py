"""App API Developer Incident Tracker — track and manage API incidents."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str  # "critical", "major", "minor"
    status: str = "open"  # "open", "investigating", "resolved"
    affected_endpoints: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None
    root_cause: str = ""

    @property
    def duration_minutes(self) -> float:
        end = self.resolved_at or time.time()
        return round((end - self.created_at) / 60, 1)

class AppAPIDeveloperAPIIncidentTracker:
    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], Incident] = {}

    def create(self, installation_id: str, incident_id: str, title: str, severity: str, affected_endpoints: list[str] | None = None) -> Incident:
        if not installation_id: raise ValueError("installation_id is required")
        if severity not in ("critical", "major", "minor"): raise ValueError("invalid severity")
        key = (installation_id, incident_id)
        if key in self._incidents: raise ValueError(f"Incident {incident_id} already exists")
        i = Incident(incident_id=incident_id, title=title, severity=severity, affected_endpoints=affected_endpoints or [])
        self._incidents[key] = i
        return i

    def update_status(self, installation_id: str, incident_id: str, status: str, root_cause: str = "") -> Incident:
        i = self._get(installation_id, incident_id)
        if status not in ("open", "investigating", "resolved"): raise ValueError("invalid status")
        i.status = status
        if root_cause: i.root_cause = root_cause
        if status == "resolved": i.resolved_at = time.time()
        return i

    def open_incidents(self, installation_id: str) -> list[Incident]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.status != "resolved"]

    def resolved(self, installation_id: str) -> list[Incident]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.status == "resolved"]

    def mttr_minutes(self, installation_id: str) -> float:
        resolved = self.resolved(installation_id)
        if not resolved: return 0.0
        return round(sum(i.duration_minutes for i in resolved) / len(resolved), 1)

    def _get(self, installation_id: str, incident_id: str) -> Incident:
        key = (installation_id, incident_id)
        i = self._incidents.get(key)
        if i is None: raise KeyError(f"Incident {incident_id} not found")
        return i
