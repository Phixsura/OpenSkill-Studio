"""App API Developer Platform Incident Response — structured incident response workflow."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

STATUSES = ["detected", "triaging", "mitigating", "monitoring", "resolved"]

@dataclass
class IncidentResponse:
    incident_id: str
    title: str
    severity: str  # "sev1", "sev2", "sev3"
    status: str = "detected"
    commander: str = ""
    affected_services: list[str] = field(default_factory=list)
    detected_at: float = field(default_factory=time.time)
    resolved_at: float | None = None

    @property
    def duration_minutes(self) -> float:
        end = self.resolved_at or time.time()
        return round((end - self.detected_at) / 60, 1)

    @property
    def resolved(self) -> bool:
        return self.status == "resolved"

class AppAPIDeveloperPlatformSDKApiDeveloperApiApiPlatformIncidentResponse:
    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], IncidentResponse] = {}

    def declare(self, installation_id: str, incident_id: str, title: str, severity: str, commander: str, affected_services: list[str] | None = None) -> IncidentResponse:
        if not installation_id: raise ValueError("installation_id is required")
        if severity not in ("sev1", "sev2", "sev3"): raise ValueError("invalid severity")
        key = (installation_id, incident_id)
        if key in self._incidents: raise ValueError(f"Incident {incident_id} exists")
        i = IncidentResponse(incident_id=incident_id, title=title, severity=severity, commander=commander, affected_services=affected_services or [])
        self._incidents[key] = i
        return i

    def advance(self, installation_id: str, incident_id: str) -> IncidentResponse:
        i = self._get(installation_id, incident_id)
        idx = STATUSES.index(i.status)
        if idx < len(STATUSES) - 1:
            i.status = STATUSES[idx + 1]
            if i.status == "resolved": i.resolved_at = time.time()
        return i

    def active_incidents(self, installation_id: str) -> list[IncidentResponse]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id and not i.resolved]

    def mttr_minutes(self, installation_id: str) -> float:
        resolved = [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.resolved]
        if not resolved: return 0.0
        return round(sum(i.duration_minutes for i in resolved) / len(resolved), 1)

    def all_incidents(self, installation_id: str) -> list[IncidentResponse]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id]

    def _get(self, installation_id: str, incident_id: str) -> IncidentResponse:
        key = (installation_id, incident_id)
        i = self._incidents.get(key)
        if i is None: raise KeyError(f"Incident {incident_id} not found")
        return i
