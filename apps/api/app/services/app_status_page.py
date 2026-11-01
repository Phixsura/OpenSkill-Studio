"""App Status Page — public status page data.

Manages status page components:
- Register components with status
- Incident reporting
- Overall system status calculation
- Per-installation scoped pages
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ComponentStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"


@dataclass
class StatusComponent:
    """A status page component."""

    component_id: str
    name: str
    status: ComponentStatus = ComponentStatus.OPERATIONAL
    description: str = ""


@dataclass
class StatusIncident:
    """A status page incident."""

    incident_id: str
    title: str
    status: str  # "investigating", "identified", "monitoring", "resolved"
    affected_components: list[str] = field(default_factory=list)
    message: str = ""

_STATUS_SEVERITY = {
    ComponentStatus.OPERATIONAL: 0,
    ComponentStatus.DEGRADED: 1,
    ComponentStatus.PARTIAL_OUTAGE: 2,
    ComponentStatus.MAJOR_OUTAGE: 3,
}


class AppStatusPage:
    """Public status page data."""

    def __init__(self) -> None:
        self._components: dict[tuple[str, str], StatusComponent] = {}
        self._incidents: dict[tuple[str, str], StatusIncident] = {}

    def add_component(
        self, installation_id: str, component_id: str, name: str,
        description: str = "",
    ) -> StatusComponent:
        if not installation_id:
            raise ValueError("installation_id is required")
        comp = StatusComponent(component_id=component_id, name=name, description=description)
        self._components[(installation_id, component_id)] = comp
        return comp

    def update_status(
        self, installation_id: str, component_id: str, status: ComponentStatus,
    ) -> StatusComponent:
        comp = self._get_component(installation_id, component_id)
        comp.status = status
        return comp

    def add_incident(
        self, installation_id: str, incident_id: str, title: str,
        affected_components: list[str] | None = None, message: str = "",
    ) -> StatusIncident:
        if not installation_id:
            raise ValueError("installation_id is required")
        incident = StatusIncident(
            incident_id=incident_id, title=title, status="investigating",
            affected_components=affected_components or [], message=message,
        )
        self._incidents[(installation_id, incident_id)] = incident
        return incident

    def resolve_incident(self, installation_id: str, incident_id: str) -> StatusIncident:
        key = (installation_id, incident_id)
        inc = self._incidents.get(key)
        if inc is None:
            raise KeyError(f"Incident {incident_id} not found")
        inc.status = "resolved"
        return inc

    def overall_status(self, installation_id: str) -> ComponentStatus:
        """Calculate worst status across all components."""
        components = self.list_components(installation_id)
        if not components:
            return ComponentStatus.OPERATIONAL
        worst = max(components, key=lambda c: _STATUS_SEVERITY[c.status])
        return worst.status

    def list_components(self, installation_id: str) -> list[StatusComponent]:
        return [c for (inst, _), c in self._components.items() if inst == installation_id]

    def active_incidents(self, installation_id: str) -> list[StatusIncident]:
        return [
            i for (inst, _), i in self._incidents.items()
            if inst == installation_id and i.status != "resolved"
        ]

    def _get_component(self, installation_id: str, component_id: str) -> StatusComponent:
        key = (installation_id, component_id)
        c = self._components.get(key)
        if c is None:
            raise KeyError(f"Component {component_id} not found")
        return c
