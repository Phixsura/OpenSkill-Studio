"""Incident Timeline — track and display platform incident history."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class IncidentEvent:
    event_id: str
    incident_id: str
    status: str  # investigating, identified, monitoring, resolved
    message: str
    timestamp: float = 0.0
    def __post_init__(self):
        if not self.timestamp: self.timestamp = time.time()


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str  # minor, major, critical
    events: list[IncidentEvent] = field(default_factory=list)
    resolved: bool = False
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class IncidentTimelineService:
    def __init__(self):
        self._incidents: dict[str, Incident] = {}
        self._counter = 0

    def create(self, title: str, severity: str) -> Incident:
        self._counter += 1
        iid = f"inc-{self._counter}"
        eid = f"evt-{self._counter}-1"
        inc = Incident(incident_id=iid, title=title, severity=severity)
        inc.events.append(IncidentEvent(event_id=eid, incident_id=iid,
                                        status="investigating", message=f"Investigating: {title}"))
        self._incidents[iid] = inc
        return inc

    def add_update(self, incident_id: str, status: str, message: str) -> IncidentEvent | None:
        inc = self._incidents.get(incident_id)
        if not inc or inc.resolved:
            return None
        self._counter += 1
        eid = f"evt-{self._counter}"
        evt = IncidentEvent(event_id=eid, incident_id=incident_id, status=status, message=message)
        inc.events.append(evt)
        if status == "resolved":
            inc.resolved = True
        return evt

    def get_active(self) -> list[Incident]:
        return [i for i in self._incidents.values() if not i.resolved]

    def get_history(self, limit: int = 20) -> list[Incident]:
        return sorted(self._incidents.values(), key=lambda i: i.created_at, reverse=True)[:limit]
