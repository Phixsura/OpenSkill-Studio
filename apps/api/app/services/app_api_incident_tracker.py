"""App API Incident Tracker — track and manage API incidents.

Manages incidents:
- Create incidents with severity
- Track status lifecycle
- Affected endpoint tracking
- Per-installation scoped incidents
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    MITIGATED = "mitigated"
    RESOLVED = "resolved"


@dataclass
class Incident:
    """An API incident."""

    incident_id: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    affected_endpoints: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None


class AppAPIIncidentTracker:
    """Track and manage API incidents."""

    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], Incident] = {}

    def create(
        self, installation_id: str, incident_id: str, title: str,
        severity: IncidentSeverity, affected_endpoints: list[str] | None = None,
    ) -> Incident:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, incident_id)
        if key in self._incidents:
            raise ValueError(f"Incident {incident_id} already exists")

        inc = Incident(
            incident_id=incident_id, title=title, severity=severity,
            affected_endpoints=affected_endpoints or [],
        )
        self._incidents[key] = inc
        return inc

    def update_status(self, installation_id: str, incident_id: str, status: IncidentStatus) -> Incident:
        inc = self._get(installation_id, incident_id)
        inc.status = status
        if status == IncidentStatus.RESOLVED:
            inc.resolved_at = time.time()
        return inc

    def active_incidents(self, installation_id: str) -> list[Incident]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.status != IncidentStatus.RESOLVED]

    def list_incidents(self, installation_id: str) -> list[Incident]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id]

    def _get(self, installation_id: str, incident_id: str) -> Incident:
        key = (installation_id, incident_id)
        i = self._incidents.get(key)
        if i is None:
            raise KeyError(f"Incident {incident_id} not found")
        return i
