"""App Incident Tracker — manage incidents for installed apps.

Tracks incidents affecting app services:
- Incident lifecycle: investigating → identified → monitoring → resolved
- Severity levels: critical, major, minor
- Timeline updates with status transitions
- Affected component tracking
- Duration computation
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class IncidentSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"


class IncidentStatus(str, Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


@dataclass
class TimelineEntry:
    """A status update on an incident."""

    status: IncidentStatus
    message: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class Incident:
    """An incident record."""

    incident_id: str
    installation_id: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    affected_components: list[str] = field(default_factory=list)
    timeline: list[TimelineEntry] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    resolved_at: float | None = None


class AppIncidentTracker:
    """Manage incidents for installed apps."""

    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], Incident] = {}

    def create_incident(
        self,
        installation_id: str,
        incident_id: str,
        title: str,
        severity: IncidentSeverity,
        affected_components: list[str] | None = None,
        message: str = "",
        now: float | None = None,
    ) -> Incident:
        """Create a new incident."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not incident_id:
            raise ValueError("incident_id is required")
        if not title:
            raise ValueError("title is required")

        key = (installation_id, incident_id)
        if key in self._incidents:
            raise ValueError(f"Incident {incident_id} already exists")

        now = now or time.time()
        incident = Incident(
            incident_id=incident_id,
            installation_id=installation_id,
            title=title,
            severity=severity,
            affected_components=affected_components or [],
            created_at=now,
        )
        # Initial timeline entry
        incident.timeline.append(TimelineEntry(
            status=IncidentStatus.INVESTIGATING,
            message=message or f"Investigating: {title}",
            timestamp=now,
        ))
        self._incidents[key] = incident
        log.warning("incident.created", incident_id=incident_id, severity=severity.value)
        return incident

    def update_status(
        self,
        installation_id: str,
        incident_id: str,
        status: IncidentStatus,
        message: str,
        now: float | None = None,
    ) -> Incident:
        """Update incident status with a timeline entry."""
        incident = self._get(installation_id, incident_id)
        if incident.status == IncidentStatus.RESOLVED:
            raise ValueError("Cannot update a resolved incident")
        if not message:
            raise ValueError("message is required")

        now = now or time.time()
        incident.status = status
        incident.timeline.append(TimelineEntry(
            status=status, message=message, timestamp=now,
        ))

        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = now
            log.info("incident.resolved", incident_id=incident_id)

        return incident

    def get_incident(self, installation_id: str, incident_id: str) -> Incident:
        return self._get(installation_id, incident_id)

    def list_incidents(
        self,
        installation_id: str,
        active_only: bool = False,
        limit: int = 20,
    ) -> list[Incident]:
        """List incidents, newest first."""
        incidents = [
            inc for (inst, _), inc in self._incidents.items()
            if inst == installation_id
        ]
        if active_only:
            incidents = [i for i in incidents if i.status != IncidentStatus.RESOLVED]
        incidents.sort(key=lambda i: i.created_at, reverse=True)
        return incidents[:limit]

    def get_duration_seconds(self, installation_id: str, incident_id: str,
                             now: float | None = None) -> float:
        """Get incident duration in seconds."""
        incident = self._get(installation_id, incident_id)
        end = incident.resolved_at or (now or time.time())
        return max(0.0, end - incident.created_at)

    def get_affected_components(self, installation_id: str) -> list[str]:
        """Get all currently affected components across active incidents."""
        components: set[str] = set()
        for (inst, _), inc in self._incidents.items():
            if inst == installation_id and inc.status != IncidentStatus.RESOLVED:
                components.update(inc.affected_components)
        return sorted(components)

    def _get(self, installation_id: str, incident_id: str) -> Incident:
        key = (installation_id, incident_id)
        incident = self._incidents.get(key)
        if incident is None:
            raise KeyError(f"Incident {incident_id} not found")
        return incident
