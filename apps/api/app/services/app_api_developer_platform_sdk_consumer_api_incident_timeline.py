"""Consumer API Incident Timeline — incident lifecycle timeline with impact tracking."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class TimelineEvent:
    event_id: str
    incident_id: str
    event_type: str  # detected, investigating, identified, fix_deployed, monitoring, resolved
    message: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    author: str = ""


@dataclass
class IncidentImpact:
    affected_endpoints: list[str] = field(default_factory=list)
    affected_consumers: int = 0
    estimated_requests_lost: int = 0


@dataclass
class IncidentTimeline:
    incident_id: str
    title: str
    severity: str  # p1, p2, p3, p4
    impact: IncidentImpact = field(default_factory=IncidentImpact)
    events: list[TimelineEvent] = field(default_factory=list)
    status: str = "active"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str = ""


@dataclass
class IncidentTimelineManager:
    """Track incident lifecycle with detailed timeline and impact."""

    _incidents: dict[str, IncidentTimeline] = field(default_factory=dict)

    def create(self, incident_id: str, title: str, severity: str,
               impact: IncidentImpact | None = None) -> dict:
        if incident_id in self._incidents:
            raise ValueError(f"Incident {incident_id} already exists")
        if severity not in ("p1", "p2", "p3", "p4"):
            raise ValueError(f"Invalid severity: {severity}")
        incident = IncidentTimeline(
            incident_id=incident_id, title=title, severity=severity,
            impact=impact or IncidentImpact(),
        )
        incident.events.append(TimelineEvent(
            f"{incident_id}-0", incident_id, "detected", f"Incident detected: {title}",
        ))
        self._incidents[incident_id] = incident
        logger.info("incident_created", incident_id=incident_id, severity=severity)
        return {"incident_id": incident_id, "severity": severity}

    def add_event(self, incident_id: str, event_type: str, message: str,
                  author: str = "") -> dict:
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        valid = ("detected", "investigating", "identified", "fix_deployed", "monitoring", "resolved")
        if event_type not in valid:
            raise ValueError(f"Invalid event type: {event_type}")
        event = TimelineEvent(
            f"{incident_id}-{len(incident.events)}", incident_id,
            event_type, message, author=author,
        )
        incident.events.append(event)
        if event_type == "resolved":
            incident.status = "resolved"
            incident.resolved_at = event.timestamp
        return {"event_id": event.event_id, "type": event_type, "status": incident.status}

    def get_timeline(self, incident_id: str) -> dict | None:
        inc = self._incidents.get(incident_id)
        if not inc:
            return None
        return {
            "incident_id": inc.incident_id, "title": inc.title,
            "severity": inc.severity, "status": inc.status,
            "impact": {
                "endpoints": inc.impact.affected_endpoints,
                "consumers": inc.impact.affected_consumers,
                "requests_lost": inc.impact.estimated_requests_lost,
            },
            "events": [
                {"event_id": e.event_id, "type": e.event_type,
                 "message": e.message, "timestamp": e.timestamp, "author": e.author}
                for e in inc.events
            ],
            "duration_events": len(inc.events),
        }

    def list_incidents(self, status: str | None = None, severity: str | None = None) -> list[dict]:
        incidents = list(self._incidents.values())
        if status:
            incidents = [i for i in incidents if i.status == status]
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        return [
            {"incident_id": i.incident_id, "title": i.title,
             "severity": i.severity, "status": i.status, "events": len(i.events)}
            for i in incidents
        ]

    def get_stats(self) -> dict:
        incs = list(self._incidents.values())
        by_severity = {s: sum(1 for i in incs if i.severity == s) for s in ("p1", "p2", "p3", "p4")}
        return {
            "total": len(incs),
            "active": sum(1 for i in incs if i.status == "active"),
            "resolved": sum(1 for i in incs if i.status == "resolved"),
            "by_severity": by_severity,
        }
