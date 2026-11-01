"""API Consumer Dashboard Widget — configurable dashboard widgets for consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DashboardWidget:
    widget_id: str
    widget_type: str  # "chart", "counter", "table", "status", "timeline"
    title: str
    data_source: str  # "requests", "errors", "latency", "webhooks", "quota"
    position: int = 0
    width: int = 1  # 1-4 columns
    config: dict[str, str] = field(default_factory=dict)

@dataclass
class Dashboard:
    dashboard_id: str
    consumer_id: str
    title: str = "API Dashboard"
    widgets: list[DashboardWidget] = field(default_factory=list)

VALID_TYPES = {"chart", "counter", "table", "status", "timeline", "gauge", "heatmap"}
VALID_SOURCES = {"requests", "errors", "latency", "webhooks", "quota", "billing", "health"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerDashboardWidget:
    def __init__(self) -> None:
        self._dashboards: dict[tuple[str, str], Dashboard] = {}

    def create_dashboard(self, installation_id: str, dashboard: Dashboard) -> Dashboard:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, dashboard.dashboard_id)
        if key in self._dashboards: raise ValueError(f"Dashboard {dashboard.dashboard_id} exists")
        self._dashboards[key] = dashboard
        return dashboard

    def add_widget(self, installation_id: str, dashboard_id: str, widget: DashboardWidget) -> Dashboard:
        d = self._get(installation_id, dashboard_id)
        if widget.widget_type not in VALID_TYPES: raise ValueError(f"Invalid type: {widget.widget_type}")
        if widget.data_source not in VALID_SOURCES: raise ValueError(f"Invalid source: {widget.data_source}")
        if not 1 <= widget.width <= 4: raise ValueError("Width must be 1-4")
        d.widgets.append(widget)
        return d

    def remove_widget(self, installation_id: str, dashboard_id: str, widget_id: str) -> Dashboard:
        d = self._get(installation_id, dashboard_id)
        d.widgets = [w for w in d.widgets if w.widget_id != widget_id]
        return d

    def list_dashboards(self, installation_id: str, consumer_id: str | None = None) -> list[Dashboard]:
        dashes = [d for (inst, _), d in self._dashboards.items() if inst == installation_id]
        if consumer_id: dashes = [d for d in dashes if d.consumer_id == consumer_id]
        return dashes

    def _get(self, installation_id: str, dashboard_id: str) -> Dashboard:
        d = self._dashboards.get((installation_id, dashboard_id))
        if d is None: raise KeyError(f"Dashboard {dashboard_id} not found")
        return d
