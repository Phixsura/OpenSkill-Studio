"""Consumer API Dashboard Widget — configurable dashboard widgets per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DashboardWidget:
    widget_id: str
    widget_type: str  # "metric", "chart", "table", "status", "alert"
    title: str
    config: dict[str, str] = field(default_factory=dict)
    position: int = 0
    width: int = 1  # 1-4 columns
    visible: bool = True

@dataclass
class Dashboard:
    consumer_id: str
    widgets: list[DashboardWidget] = field(default_factory=list)
    layout: str = "grid"  # "grid", "list"

VALID_WIDGET_TYPES = {"metric", "chart", "table", "status", "alert", "log", "heatmap"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerDashboardWidget:
    def __init__(self) -> None:
        self._dashboards: dict[tuple[str, str], Dashboard] = {}

    def add_widget(self, installation_id: str, consumer_id: str, widget: DashboardWidget) -> DashboardWidget:
        if not installation_id:
            raise ValueError("installation_id is required")
        if widget.widget_type not in VALID_WIDGET_TYPES:
            raise ValueError(f"Invalid widget_type: {widget.widget_type}")
        if not (1 <= widget.width <= 4):
            raise ValueError("width must be 1-4")
        key = (installation_id, consumer_id)
        if key not in self._dashboards:
            self._dashboards[key] = Dashboard(consumer_id=consumer_id)
        dash = self._dashboards[key]
        if any(w.widget_id == widget.widget_id for w in dash.widgets):
            raise ValueError(f"Widget {widget.widget_id} already exists")
        dash.widgets.append(widget)
        dash.widgets.sort(key=lambda w: w.position)
        return widget

    def remove_widget(self, installation_id: str, consumer_id: str, widget_id: str) -> None:
        key = (installation_id, consumer_id)
        dash = self._dashboards.get(key)
        if not dash:
            raise ValueError("Dashboard not found")
        before = len(dash.widgets)
        dash.widgets = [w for w in dash.widgets if w.widget_id != widget_id]
        if len(dash.widgets) == before:
            raise ValueError("Widget not found")

    def reorder(self, installation_id: str, consumer_id: str, widget_ids: list[str]) -> list[DashboardWidget]:
        key = (installation_id, consumer_id)
        dash = self._dashboards.get(key)
        if not dash:
            raise ValueError("Dashboard not found")
        by_id = {w.widget_id: w for w in dash.widgets}
        for i, wid in enumerate(widget_ids):
            if wid in by_id:
                by_id[wid].position = i
        dash.widgets.sort(key=lambda w: w.position)
        return dash.widgets

    def get_dashboard(self, installation_id: str, consumer_id: str) -> Dashboard | None:
        return self._dashboards.get((installation_id, consumer_id))

    def get_visible_widgets(self, installation_id: str, consumer_id: str) -> list[DashboardWidget]:
        dash = self._dashboards.get((installation_id, consumer_id))
        if not dash:
            return []
        return [w for w in dash.widgets if w.visible]
