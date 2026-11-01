"""Incident Manager — incident lifecycle with severity and timeline."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

SEVERITIES = ("critical", "high", "medium", "low")
STATUSES = ("open", "investigating", "identified", "monitoring", "resolved")


@dataclass
class TimelineEntry:
    timestamp: str
    status: str
    message: str
    author: str = ""


@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str
    status: str = "open"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    resolved_at: str | None = None
    affected_endpoints: list[str] = field(default_factory=list)
    timeline: list[TimelineEntry] = field(default_factory=list)


@dataclass
class IncidentManager:
    """Manage incident lifecycle with severity tracking."""

    _incidents: dict[str, Incident] = field(default_factory=dict)

    def create(self, incident_id: str, title: str, severity: str,
               affected_endpoints: list[str] | None = None) -> dict:
        if severity not in SEVERITIES:
            raise ValueError(f"Invalid severity: {severity}. Must be one of {SEVERITIES}")
        if incident_id in self._incidents:
            raise ValueError(f"Incident {incident_id} already exists")
        incident = Incident(
            incident_id=incident_id, title=title, severity=severity,
            affected_endpoints=affected_endpoints or [],
        )
        incident.timeline.append(TimelineEntry(
            timestamp=incident.created_at, status="open", message="Incident created",
        ))
        self._incidents[incident_id] = incident
        logger.info("incident_created", incident_id=incident_id, severity=severity)
        return {"incident_id": incident_id, "severity": severity, "status": "open"}

    def update_status(self, incident_id: str, status: str, message: str = "",
                      author: str = "") -> dict:
        incident = self._incidents.get(incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")
        if status not in STATUSES:
            raise ValueError(f"Invalid status: {status}")
        if incident.status == "resolved" and status != "open":
            raise ValueError("Resolved incident can only be reopened")
        incident.status = status
        if status == "resolved":
            incident.resolved_at = datetime.now(timezone.utc).isoformat()
        incident.timeline.append(TimelineEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            status=status, message=message, author=author,
        ))
        logger.info("incident_updated", incident_id=incident_id, status=status)
        return {"incident_id": incident_id, "status": status}

    def get_incident(self, incident_id: str) -> dict | None:
        inc = self._incidents.get(incident_id)
        if not inc:
            return None
        return {
            "incident_id": inc.incident_id, "title": inc.title,
            "severity": inc.severity, "status": inc.status,
            "created_at": inc.created_at, "resolved_at": inc.resolved_at,
            "affected_endpoints": inc.affected_endpoints,
            "timeline_count": len(inc.timeline),
        }

    def list_incidents(self, status: str | None = None,
                       severity: str | None = None) -> list[dict]:
        results = []
        for inc in self._incidents.values():
            if status and inc.status != status:
                continue
            if severity and inc.severity != severity:
                continue
            results.append(self.get_incident(inc.incident_id))
        return sorted(results, key=lambda x: x["created_at"], reverse=True)

    def get_timeline(self, incident_id: str) -> list[dict]:
        inc = self._incidents.get(incident_id)
        if not inc:
            return []
        return [{"timestamp": e.timestamp, "status": e.status,
                 "message": e.message, "author": e.author}
                for e in inc.timeline]

    def get_stats(self) -> dict:
        all_inc = list(self._incidents.values())
        open_count = sum(1 for i in all_inc if i.status != "resolved")
        by_severity = {}
        for s in SEVERITIES:
            by_severity[s] = sum(1 for i in all_inc if i.severity == s and i.status != "resolved")
        return {
            "total": len(all_inc),
            "open": open_count,
            "resolved": len(all_inc) - open_count,
            "by_severity": by_severity,
        }
