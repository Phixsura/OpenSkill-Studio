"""Incident Manager — track and coordinate extension incident response.

Manages incidents with severity levels, timeline events, status
tracking, assignees, postmortem generation, and MTTR calculation.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class IncidentSeverity(str, Enum):
    SEV1 = "sev1"  # critical, total outage
    SEV2 = "sev2"  # major degradation
    SEV3 = "sev3"  # minor issue
    SEV4 = "sev4"  # cosmetic / low impact


class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MITIGATING = "mitigating"
    RESOLVED = "resolved"
    POSTMORTEM = "postmortem"


@dataclass
class TimelineEvent:
    message: str
    author: str
    status: IncidentStatus
    timestamp: float = 0.0

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = time.time()


@dataclass
class Incident:
    incident_id: str
    extension_id: str
    title: str
    severity: IncidentSeverity
    status: IncidentStatus = IncidentStatus.OPEN
    assignee: str = ""
    timeline: list[TimelineEvent] = field(default_factory=list)
    affected_users: int = 0
    root_cause: str = ""
    created_at: float = 0.0
    resolved_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()

    @property
    def mttr_minutes(self) -> float:
        if self.resolved_at and self.created_at:
            return round((self.resolved_at - self.created_at) / 60, 1)
        return 0


class IncidentManagerService:
    """Manages extension incidents with timeline and MTTR tracking."""

    def __init__(self):
        self._incidents: dict[str, Incident] = {}

    def create(self, extension_id: str, title: str,
               severity: IncidentSeverity,
               affected_users: int = 0) -> Incident:
        incident_id = f"inc_{secrets.token_urlsafe(10)}"
        incident = Incident(
            incident_id=incident_id, extension_id=extension_id,
            title=title, severity=severity, affected_users=affected_users,
        )
        incident.timeline.append(TimelineEvent(
            message=f"Incident created: {title}",
            author="system", status=IncidentStatus.OPEN,
        ))
        self._incidents[incident_id] = incident
        return incident

    def assign(self, incident_id: str, assignee: str) -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.assignee = assignee
        inc.timeline.append(TimelineEvent(
            message=f"Assigned to {assignee}",
            author="system", status=inc.status,
        ))
        return True

    def update_status(self, incident_id: str, status: IncidentStatus,
                      message: str, author: str) -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.status = status
        inc.timeline.append(TimelineEvent(
            message=message, author=author, status=status,
        ))
        if status == IncidentStatus.RESOLVED:
            inc.resolved_at = time.time()
        return True

    def set_root_cause(self, incident_id: str, root_cause: str) -> bool:
        inc = self._incidents.get(incident_id)
        if not inc:
            return False
        inc.root_cause = root_cause
        return True

    def get_mttr(self, extension_id: str) -> dict:
        resolved = [inc for inc in self._incidents.values()
                    if inc.extension_id == extension_id
                    and inc.status == IncidentStatus.RESOLVED]
        if not resolved:
            return {"avg_minutes": 0, "count": 0}
        mttrs = [inc.mttr_minutes for inc in resolved]
        return {
            "avg_minutes": round(sum(mttrs) / len(mttrs), 1),
            "count": len(resolved),
            "min_minutes": min(mttrs),
            "max_minutes": max(mttrs),
        }

    def list_incidents(self, extension_id: str,
                       status: IncidentStatus | None = None) -> list[Incident]:
        incs = [i for i in self._incidents.values() if i.extension_id == extension_id]
        if status:
            incs = [i for i in incs if i.status == status]
        return sorted(incs, key=lambda i: i.created_at, reverse=True)

    def get_summary(self, extension_id: str) -> dict:
        incs = [i for i in self._incidents.values() if i.extension_id == extension_id]
        by_sev: dict[str, int] = defaultdict(int)
        for i in incs:
            by_sev[i.severity.value] += 1
        open_count = sum(1 for i in incs if i.status != IncidentStatus.RESOLVED)
        return {
            "total": len(incs), "open": open_count,
            "by_severity": dict(by_sev),
            "mttr": self.get_mttr(extension_id),
        }
