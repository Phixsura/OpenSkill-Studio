"""API Status Page — aggregate service status for public status page."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class ServiceStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"

@dataclass
class ServiceComponent:
    component_id: str
    name: str
    status: ServiceStatus = ServiceStatus.OPERATIONAL
    description: str = ""
    updated_at: float = field(default_factory=time.time)

@dataclass
class Incident:
    incident_id: str
    title: str
    status: str  # "investigating", "identified", "monitoring", "resolved"
    impact: ServiceStatus
    components: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiStatusPage:
    def __init__(self) -> None:
        self._components: dict[tuple[str, str], ServiceComponent] = {}
        self._incidents: dict[tuple[str, str], Incident] = {}

    def add_component(self, installation_id: str, component: ServiceComponent) -> ServiceComponent:
        if not installation_id: raise ValueError("installation_id is required")
        self._components[(installation_id, component.component_id)] = component
        return component

    def update_status(self, installation_id: str, component_id: str, status: ServiceStatus) -> ServiceComponent:
        key = (installation_id, component_id)
        c = self._components.get(key)
        if c is None: raise KeyError(f"Component {component_id} not found")
        c.status = status
        c.updated_at = time.time()
        return c

    def overall_status(self, installation_id: str) -> ServiceStatus:
        components = [c for (inst, _), c in self._components.items() if inst == installation_id]
        if not components: return ServiceStatus.OPERATIONAL
        statuses = [c.status for c in components]
        if ServiceStatus.MAJOR_OUTAGE in statuses: return ServiceStatus.MAJOR_OUTAGE
        if ServiceStatus.PARTIAL_OUTAGE in statuses: return ServiceStatus.PARTIAL_OUTAGE
        if ServiceStatus.DEGRADED in statuses: return ServiceStatus.DEGRADED
        if ServiceStatus.MAINTENANCE in statuses: return ServiceStatus.MAINTENANCE
        return ServiceStatus.OPERATIONAL

    def create_incident(self, installation_id: str, incident: Incident) -> Incident:
        if not installation_id: raise ValueError("installation_id is required")
        self._incidents[(installation_id, incident.incident_id)] = incident
        return incident

    def active_incidents(self, installation_id: str) -> list[Incident]:
        return [i for (inst, _), i in self._incidents.items() if inst == installation_id and i.status != "resolved"]

    def list_components(self, installation_id: str) -> list[ServiceComponent]:
        return [c for (inst, _), c in self._components.items() if inst == installation_id]
