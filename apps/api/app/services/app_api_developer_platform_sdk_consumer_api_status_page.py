"""Consumer API Status Page — public status page with component health."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()

COMPONENT_STATUSES = ("operational", "degraded_performance", "partial_outage", "major_outage", "maintenance")


@dataclass
class Component:
    component_id: str
    name: str
    group: str = ""
    status: str = "operational"
    description: str = ""


@dataclass
class MaintenanceWindow:
    maintenance_id: str
    title: str
    start_time: str
    end_time: str
    affected_components: list[str] = field(default_factory=list)
    status: str = "scheduled"  # scheduled, in_progress, completed


@dataclass
class StatusPage:
    """Manage public API status page with component health."""

    _components: dict[str, Component] = field(default_factory=dict)
    _maintenances: dict[str, MaintenanceWindow] = field(default_factory=dict)
    _history: list[dict] = field(default_factory=list)

    def add_component(self, component: Component) -> dict:
        if component.component_id in self._components:
            raise ValueError(f"Component {component.component_id} already exists")
        if component.status not in COMPONENT_STATUSES:
            raise ValueError(f"Invalid status: {component.status}")
        self._components[component.component_id] = component
        return {"component_id": component.component_id, "name": component.name}

    def update_status(self, component_id: str, status: str, message: str = "") -> dict:
        comp = self._components.get(component_id)
        if not comp:
            raise ValueError(f"Component {component_id} not found")
        if status not in COMPONENT_STATUSES:
            raise ValueError(f"Invalid status: {status}")
        old = comp.status
        comp.status = status
        if old != status:
            self._history.append({
                "component_id": component_id, "from": old, "to": status,
                "message": message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            logger.info("status_updated", component=component_id, status=status)
        return {"component_id": component_id, "status": status, "changed": old != status}

    def schedule_maintenance(self, maint: MaintenanceWindow) -> dict:
        if maint.maintenance_id in self._maintenances:
            raise ValueError(f"Maintenance {maint.maintenance_id} already exists")
        self._maintenances[maint.maintenance_id] = maint
        logger.info("maintenance_scheduled", id=maint.maintenance_id)
        return {"maintenance_id": maint.maintenance_id, "title": maint.title}

    def get_page(self) -> dict:
        components = list(self._components.values())
        # Overall status
        statuses = [c.status for c in components]
        if any(s == "major_outage" for s in statuses):
            overall = "major_outage"
        elif any(s == "partial_outage" for s in statuses):
            overall = "partial_outage"
        elif any(s == "degraded_performance" for s in statuses):
            overall = "degraded_performance"
        elif any(s == "maintenance" for s in statuses):
            overall = "maintenance"
        else:
            overall = "all_systems_operational"
        # Group components
        groups: dict[str, list[dict]] = {}
        for c in components:
            g = c.group or "Ungrouped"
            groups.setdefault(g, []).append({
                "id": c.component_id, "name": c.name, "status": c.status,
            })
        scheduled = [
            {"id": m.maintenance_id, "title": m.title, "start": m.start_time,
             "end": m.end_time, "status": m.status}
            for m in self._maintenances.values() if m.status != "completed"
        ]
        return {
            "overall_status": overall,
            "groups": groups,
            "component_count": len(components),
            "scheduled_maintenance": scheduled,
            "recent_updates": self._history[-5:],
        }

    def get_uptime(self) -> dict:
        total = len(self._components)
        operational = sum(1 for c in self._components.values() if c.status == "operational")
        return {
            "total": total,
            "operational": operational,
            "uptime_pct": round(operational / total * 100, 1) if total > 0 else 100,
        }
