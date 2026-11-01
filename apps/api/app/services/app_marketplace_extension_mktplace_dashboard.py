"""Marketplace Dashboard — comprehensive platform dashboard."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class DashboardWidget:
    widget_id: str
    title: str
    widget_type: str  # counter, chart, list, status
    data: dict = field(default_factory=dict)
    position: int = 0


class MktplaceDashboardService:
    def __init__(self):
        self._widgets: dict[str, list[DashboardWidget]] = {}  # user_id -> widgets
        self._counter = 0

    def add_widget(self, user_id: str, title: str, widget_type: str,
                   data: dict, position: int = -1) -> DashboardWidget:
        self._counter += 1
        widget = DashboardWidget(widget_id=f"wgt-{self._counter}", title=title,
                                 widget_type=widget_type, data=data)
        if user_id not in self._widgets:
            self._widgets[user_id] = []
        if position >= 0:
            widget.position = position
        else:
            widget.position = len(self._widgets[user_id])
        self._widgets[user_id].append(widget)
        return widget

    def get_dashboard(self, user_id: str) -> list[DashboardWidget]:
        return sorted(self._widgets.get(user_id, []), key=lambda w: w.position)

    def remove_widget(self, user_id: str, widget_id: str) -> bool:
        widgets = self._widgets.get(user_id, [])
        for i, w in enumerate(widgets):
            if w.widget_id == widget_id:
                widgets.pop(i)
                return True
        return False

    def reorder(self, user_id: str, widget_ids: list[str]) -> bool:
        widgets = self._widgets.get(user_id, [])
        by_id = {w.widget_id: w for w in widgets}
        for i, wid in enumerate(widget_ids):
            if wid in by_id:
                by_id[wid].position = i
        return True

    def get_default_dashboard(self) -> list[dict]:
        return [
            {"title": "Total Extensions", "type": "counter", "data": {"value": 0}},
            {"title": "Active Users", "type": "counter", "data": {"value": 0}},
            {"title": "Revenue", "type": "counter", "data": {"value": "$0"}},
            {"title": "System Health", "type": "status", "data": {"status": "operational"}},
        ]
