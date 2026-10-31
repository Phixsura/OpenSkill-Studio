"""Consumer Incident Tracker — track and manage API incidents affecting consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class Incident:
    incident_id: str
    title: str
    severity: str = "minor"  # "minor", "major", "critical"
    status: str = "investigating"  # "investigating", "identified", "monitoring", "resolved"
    affected_endpoints: list[str] = field(default_factory=list)
    affected_consumers: list[str] = field(default_factory=list)  # empty = all
    created_at: datetime | None = None
    resolved_at: datetime | None = None

@dataclass
class IncidentUpdate:
    update_id: str
    incident_id: str
    message: str
    status: str
    timestamp: datetime

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerIncidentTracker:
    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], Incident] = {}
        self._updates: dict[tuple[str, str], list[IncidentUpdate]] = {}

    def create(self, installation_id: str, incident: Incident) -> Incident:
        if not installation_id:
            raise ValueError("installation_id is required")
        if incident.severity not in ("minor", "major", "critical"):
            raise ValueError(f"Invalid severity: {incident.severity}")
        incident.created_at = incident.created_at or datetime.utcnow()
        self._incidents[(installation_id, incident.incident_id)] = incident
        log.info("incident_created", installation_id=installation_id, id=incident.incident_id, severity=incident.severity)
        return incident

    def update_status(self, installation_id: str, incident_id: str, update: IncidentUpdate) -> Incident:
        key = (installation_id, incident_id)
        incident = self._incidents.get(key)
        if not incident:
            raise ValueError("Incident not found")
        if incident.status == "resolved":
            raise ValueError("Cannot update resolved incident")
        incident.status = update.status
        if update.status == "resolved":
            incident.resolved_at = update.timestamp
        if key not in self._updates:
            self._updates[key] = []
        self._updates[key].append(update)
        return incident

    def get(self, installation_id: str, incident_id: str) -> Incident | None:
        return self._incidents.get((installation_id, incident_id))

    def active_incidents(self, installation_id: str, consumer_id: str | None = None) -> list[Incident]:
        active = [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.status != "resolved"]
        if consumer_id:
            active = [i for i in active if not i.affected_consumers or consumer_id in i.affected_consumers]
        return sorted(active, key=lambda i: {"critical": 0, "major": 1, "minor": 2}.get(i.severity, 3))

    def get_updates(self, installation_id: str, incident_id: str) -> list[IncidentUpdate]:
        return self._updates.get((installation_id, incident_id), [])
