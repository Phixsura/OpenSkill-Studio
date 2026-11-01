"""App Status Page Builder — generate public status pages for installed apps.

Builds a structured status page from component health data:
- Component status rollup (operational, degraded, partial outage, major outage)
- Overall system status computation
- Active incident embedding
- Uptime metrics per component
- Maintenance window scheduling
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class ComponentStatus(str, Enum):
    OPERATIONAL = "operational"
    DEGRADED = "degraded"
    PARTIAL_OUTAGE = "partial_outage"
    MAJOR_OUTAGE = "major_outage"
    MAINTENANCE = "maintenance"


class SystemStatus(str, Enum):
    ALL_OPERATIONAL = "all_operational"
    MINOR_ISSUES = "minor_issues"
    MAJOR_ISSUES = "major_issues"
    OUTAGE = "outage"


@dataclass
class StatusComponent:
    """A component on the status page."""

    name: str
    status: ComponentStatus
    uptime_pct: float = 100.0
    description: str = ""


@dataclass
class MaintenanceWindow:
    """A scheduled maintenance window."""

    title: str
    scheduled_start: datetime
    scheduled_end: datetime
    affected_components: list[str]
    description: str = ""

    @property
    def is_active(self) -> bool:
        now = datetime.now(UTC)
        return self.scheduled_start <= now <= self.scheduled_end

    @property
    def is_upcoming(self) -> bool:
        return datetime.now(UTC) < self.scheduled_start


@dataclass
class ActiveIncident:
    """An incident shown on the status page."""

    title: str
    status: str
    severity: str
    started_at: datetime
    last_update: str


@dataclass
class StatusPage:
    """A complete status page."""

    app_name: str
    system_status: SystemStatus
    components: list[StatusComponent]
    active_incidents: list[ActiveIncident]
    maintenance_windows: list[MaintenanceWindow]
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))


STATUS_PRIORITY = {
    ComponentStatus.MAJOR_OUTAGE: 4,
    ComponentStatus.PARTIAL_OUTAGE: 3,
    ComponentStatus.DEGRADED: 2,
    ComponentStatus.MAINTENANCE: 1,
    ComponentStatus.OPERATIONAL: 0,
}


class AppStatusPageBuilder:
    """Build status pages from component data."""

    def __init__(self):
        self._components: dict[str, list[StatusComponent]] = {}
        self._incidents: dict[str, list[ActiveIncident]] = {}
        self._maintenance: dict[str, list[MaintenanceWindow]] = {}

    def set_components(self, app_id: str, components: list[StatusComponent]) -> None:
        self._components[app_id] = components

    def set_incidents(self, app_id: str, incidents: list[ActiveIncident]) -> None:
        self._incidents[app_id] = incidents

    def add_maintenance(self, app_id: str, window: MaintenanceWindow) -> None:
        self._maintenance.setdefault(app_id, []).append(window)

    def build(self, app_id: str, app_name: str) -> StatusPage:
        """Build a complete status page."""
        components = self._components.get(app_id, [])
        incidents = self._incidents.get(app_id, [])
        maintenance = self._maintenance.get(app_id, [])

        # Apply maintenance status to affected components
        active_maint = [m for m in maintenance if m.is_active]
        for maint in active_maint:
            for comp in components:
                if comp.name in maint.affected_components:
                    comp.status = ComponentStatus.MAINTENANCE

        system_status = self._compute_system_status(components)

        return StatusPage(
            app_name=app_name,
            system_status=system_status,
            components=components,
            active_incidents=incidents,
            maintenance_windows=[m for m in maintenance if m.is_active or m.is_upcoming],
        )

    @staticmethod
    def _compute_system_status(components: list[StatusComponent]) -> SystemStatus:
        if not components:
            return SystemStatus.ALL_OPERATIONAL

        worst = max(
            (STATUS_PRIORITY.get(c.status, 0) for c in components),
            default=0,
        )

        if worst >= 4:
            return SystemStatus.OUTAGE
        elif worst >= 3:
            return SystemStatus.MAJOR_ISSUES
        elif worst >= 1:
            return SystemStatus.MINOR_ISSUES
        return SystemStatus.ALL_OPERATIONAL
