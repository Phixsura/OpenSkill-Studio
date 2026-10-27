"""App Incident Tracker — track and manage operational incidents for installed apps.

Provides incident lifecycle management:
- Incident creation with severity and affected components
- Status progression: investigating → identified → monitoring → resolved
- Timeline events per incident
- MTTR (Mean Time To Resolve) computation
- Incident history and filtering
- Impact summary per app
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class Severity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    INFO = "info"


class IncidentStatus(str, Enum):
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"


@dataclass
class TimelineEvent:
    """A status update on an incident."""

    status: IncidentStatus
    message: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    author: str = "system"


@dataclass
class Incident:
    """An operational incident."""

    incident_id: str
    app_id: str
    title: str
    severity: Severity
    status: IncidentStatus = IncidentStatus.INVESTIGATING
    affected_components: list[str] = field(default_factory=list)
    timeline: list[TimelineEvent] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None

    @property
    def duration_minutes(self) -> float | None:
        if self.resolved_at is None:
            return None
        return (self.resolved_at - self.created_at).total_seconds() / 60


@dataclass
class IncidentSummary:
    """Summary statistics for an app's incidents."""

    app_id: str
    total: int
    open: int
    resolved: int
    mttr_minutes: float | None  # mean time to resolve
    by_severity: dict[str, int]


class AppIncidentTracker:
    """Track and manage app incidents."""

    def __init__(self):
        self._incidents: dict[str, Incident] = {}
        self._next_id = 0

    def create(self, app_id: str, title: str, severity: Severity,
               affected_components: list[str] | None = None,
               author: str = "system") -> Incident:
        """Create a new incident."""
        if not title:
            raise ValueError("Incident title is required")

        self._next_id += 1
        iid = f"inc-{self._next_id}"
        incident = Incident(
            incident_id=iid, app_id=app_id, title=title,
            severity=severity,
            affected_components=affected_components or [],
        )
        incident.timeline.append(TimelineEvent(
            status=IncidentStatus.INVESTIGATING,
            message=f"Incident created: {title}",
            author=author,
        ))
        self._incidents[iid] = incident
        log.warning("incident.created", incident_id=iid, app_id=app_id,
                     severity=severity.value)
        return incident

    def update_status(self, incident_id: str, status: IncidentStatus,
                      message: str, author: str = "system") -> Incident | None:
        """Update incident status with a timeline event."""
        incident = self._incidents.get(incident_id)
        if incident is None:
            return None
        if incident.status == IncidentStatus.RESOLVED:
            return None  # can't update resolved incidents

        incident.status = status
        incident.timeline.append(TimelineEvent(
            status=status, message=message, author=author,
        ))

        if status == IncidentStatus.RESOLVED:
            incident.resolved_at = datetime.now(UTC)
            log.info("incident.resolved", incident_id=incident_id,
                     duration_min=round(incident.duration_minutes or 0, 1))

        return incident

    def get(self, incident_id: str) -> Incident | None:
        return self._incidents.get(incident_id)

    def list_incidents(self, app_id: str | None = None,
                       status: IncidentStatus | None = None,
                       severity: Severity | None = None,
                       limit: int = 50) -> list[Incident]:
        results = list(self._incidents.values())
        if app_id:
            results = [i for i in results if i.app_id == app_id]
        if status:
            results = [i for i in results if i.status == status]
        if severity:
            results = [i for i in results if i.severity == severity]
        results.sort(key=lambda i: i.created_at, reverse=True)
        return results[:limit]

    def get_open_count(self, app_id: str) -> int:
        return len([i for i in self._incidents.values()
                    if i.app_id == app_id and i.status != IncidentStatus.RESOLVED])

    def get_summary(self, app_id: str) -> IncidentSummary:
        """Compute incident summary with MTTR."""
        app_incidents = [i for i in self._incidents.values() if i.app_id == app_id]
        resolved = [i for i in app_incidents if i.status == IncidentStatus.RESOLVED]
        open_count = len(app_incidents) - len(resolved)

        mttr = None
        if resolved:
            durations = [i.duration_minutes for i in resolved if i.duration_minutes is not None]
            if durations:
                mttr = round(sum(durations) / len(durations), 1)

        by_severity: dict[str, int] = {}
        for i in app_incidents:
            by_severity[i.severity.value] = by_severity.get(i.severity.value, 0) + 1

        return IncidentSummary(
            app_id=app_id,
            total=len(app_incidents),
            open=open_count,
            resolved=len(resolved),
            mttr_minutes=mttr,
            by_severity=by_severity,
        )
