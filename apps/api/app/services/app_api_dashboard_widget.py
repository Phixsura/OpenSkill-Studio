"""App API Dashboard Widget — manage dashboard widget configurations.

Manages dashboard widgets:
- Register widget types with data sources
- Configure widget instances
- Track widget refresh stats
- Per-installation scoped widgets
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DashboardWidget:
    """A dashboard widget configuration."""

    widget_id: str
    widget_type: str  # "chart", "metric", "table", "list"
    title: str
    data_source: str
    refresh_interval: int = 60  # seconds
    refresh_count: int = 0


class AppAPIDashboardWidget:
    """Manage dashboard widget configurations."""

    def __init__(self) -> None:
        self._widgets: dict[tuple[str, str], DashboardWidget] = {}

    def register(
        self, installation_id: str, widget_id: str, widget_type: str,
        title: str, data_source: str, refresh_interval: int = 60,
    ) -> DashboardWidget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if widget_type not in ("chart", "metric", "table", "list"):
            raise ValueError("widget_type must be chart, metric, table, or list")

        w = DashboardWidget(
            widget_id=widget_id, widget_type=widget_type, title=title,
            data_source=data_source, refresh_interval=refresh_interval,
        )
        self._widgets[(installation_id, widget_id)] = w
        return w

    def record_refresh(self, installation_id: str, widget_id: str) -> DashboardWidget:
        w = self._get(installation_id, widget_id)
        w.refresh_count += 1
        return w

    def by_type(self, installation_id: str, widget_type: str) -> list[DashboardWidget]:
        return [w for (inst, _), w in self._widgets.items() if inst == installation_id and w.widget_type == widget_type]

    def list_widgets(self, installation_id: str) -> list[DashboardWidget]:
        return [w for (inst, _), w in self._widgets.items() if inst == installation_id]

    def _get(self, installation_id: str, widget_id: str) -> DashboardWidget:
        key = (installation_id, widget_id)
        w = self._widgets.get(key)
        if w is None:
            raise KeyError(f"Widget {widget_id} not found")
        return w
