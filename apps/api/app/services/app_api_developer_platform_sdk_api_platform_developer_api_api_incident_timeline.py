"""API Incident Timeline — track incident lifecycle with timestamped updates."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class IncidentSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"

class IncidentPhase(str, Enum):
    DETECTED = "detected"
    INVESTIGATING = "investigating"
    IDENTIFIED = "identified"
    MONITORING = "monitoring"
    RESOLVED = "resolved"

@dataclass
class TimelineEntry:
    phase: IncidentPhase
    message: str
    timestamp: float = field(default_factory=time.time)
    author: str = "system"

@dataclass
class IncidentRecord:
    incident_id: str
    title: str
    severity: IncidentSeverity
    current_phase: IncidentPhase = IncidentPhase.DETECTED
    timeline: list[TimelineEntry] = field(default_factory=list)
    affected_endpoints: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    resolved_at: float = 0.0
    duration_minutes: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiIncidentTimeline:
    def __init__(self) -> None:
        self._incidents: dict[tuple[str, str], IncidentRecord] = {}

    def create_incident(self, installation_id: str, incident_id: str, title: str, severity: IncidentSeverity, affected_endpoints: list[str] | None = None) -> IncidentRecord:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, incident_id)
        if key in self._incidents: raise ValueError(f"Incident {incident_id} already exists")
        ir = IncidentRecord(incident_id=incident_id, title=title, severity=severity, affected_endpoints=affected_endpoints or [])
        ir.timeline.append(TimelineEntry(phase=IncidentPhase.DETECTED, message=f"Incident detected: {title}"))
        self._incidents[key] = ir
        return ir

    def update_phase(self, installation_id: str, incident_id: str, phase: IncidentPhase, message: str, author: str = "system") -> IncidentRecord:
        ir = self._get(installation_id, incident_id)
        phase_order = list(IncidentPhase)
        if phase_order.index(phase) < phase_order.index(ir.current_phase):
            raise ValueError(f"Cannot move backwards from {ir.current_phase.value} to {phase.value}")
        ir.current_phase = phase
        ir.timeline.append(TimelineEntry(phase=phase, message=message, author=author))
        if phase == IncidentPhase.RESOLVED:
            ir.resolved_at = time.time()
            ir.duration_minutes = round((ir.resolved_at - ir.created_at) / 60, 1)
        return ir

    def active_incidents(self, installation_id: str) -> list[IncidentRecord]:
        return [ir for (inst, _), ir in self._incidents.items() if inst == installation_id and ir.current_phase != IncidentPhase.RESOLVED]

    def resolved_incidents(self, installation_id: str) -> list[IncidentRecord]:
        return [ir for (inst, _), ir in self._incidents.items() if inst == installation_id and ir.current_phase == IncidentPhase.RESOLVED]

    def get_incident(self, installation_id: str, incident_id: str) -> IncidentRecord:
        return self._get(installation_id, incident_id)

    def _get(self, installation_id: str, incident_id: str) -> IncidentRecord:
        ir = self._incidents.get((installation_id, incident_id))
        if ir is None: raise KeyError(f"Incident {incident_id} not found")
        return ir
