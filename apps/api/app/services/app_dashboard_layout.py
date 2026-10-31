"""App Dashboard Layout — manage customizable dashboard layouts.

Manages dashboard configurations:
- Define widget layouts with positions
- Save/load user dashboard layouts
- Default layout fallback
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class DashboardWidget:
    """A widget on a dashboard."""

    widget_id: str
    widget_type: str
    title: str
    col: int = 0
    row: int = 0
    width: int = 1
    height: int = 1
    config: dict = field(default_factory=dict)


@dataclass
class DashboardLayout:
    """A dashboard layout."""

    layout_id: str
    name: str
    widgets: list[DashboardWidget]
    is_default: bool = False


class AppDashboardLayout:
    """Manage customizable dashboard layouts."""

    def __init__(self) -> None:
        self._layouts: dict[tuple[str, str], DashboardLayout] = {}

    def save_layout(
        self, installation_id: str, layout_id: str, name: str,
        widgets: list[dict], is_default: bool = False,
    ) -> DashboardLayout:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not layout_id:
            raise ValueError("layout_id is required")

        widget_objs = [
            DashboardWidget(
                widget_id=w["widget_id"], widget_type=w["type"],
                title=w.get("title", ""), col=w.get("col", 0), row=w.get("row", 0),
                width=w.get("width", 1), height=w.get("height", 1),
            )
            for w in widgets
        ]

        layout = DashboardLayout(
            layout_id=layout_id, name=name,
            widgets=widget_objs, is_default=is_default,
        )
        self._layouts[(installation_id, layout_id)] = layout
        return layout

    def get_layout(self, installation_id: str, layout_id: str) -> DashboardLayout:
        key = (installation_id, layout_id)
        l = self._layouts.get(key)
        if l is None:
            raise KeyError(f"Layout {layout_id} not found")
        return l

    def get_default(self, installation_id: str) -> DashboardLayout | None:
        for (inst, _), l in self._layouts.items():
            if inst == installation_id and l.is_default:
                return l
        return None

    def list_layouts(self, installation_id: str) -> list[DashboardLayout]:
        return [l for (inst, _), l in self._layouts.items() if inst == installation_id]

    def widget_count(self, installation_id: str, layout_id: str) -> int:
        return len(self.get_layout(installation_id, layout_id).widgets)
