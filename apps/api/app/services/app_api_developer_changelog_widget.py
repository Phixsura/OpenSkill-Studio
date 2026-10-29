"""App API Developer Changelog Widget — embeddable widget management."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogWidget:
    widget_id: str
    position: str  # "bottom-right", "bottom-left", "top-right"
    trigger: str  # "bell", "badge", "text"
    max_items: int = 5
    theme: str = "auto"
    impressions: int = 0
    clicks: int = 0

    @property
    def ctr(self) -> float:
        if self.impressions == 0: return 0.0
        return round(self.clicks / self.impressions * 100, 1)

VALID_POSITIONS = {"bottom-right", "bottom-left", "top-right", "top-left"}
VALID_TRIGGERS = {"bell", "badge", "text", "dot"}

class AppAPIDeveloperChangelogWidget:
    def __init__(self) -> None:
        self._widgets: dict[str, ChangelogWidget] = {}

    def configure(self, installation_id: str, widget_id: str, position: str = "bottom-right", trigger: str = "bell", max_items: int = 5, theme: str = "auto") -> ChangelogWidget:
        if not installation_id: raise ValueError("installation_id is required")
        if position not in VALID_POSITIONS: raise ValueError(f"position must be one of {VALID_POSITIONS}")
        if trigger not in VALID_TRIGGERS: raise ValueError(f"trigger must be one of {VALID_TRIGGERS}")
        w = ChangelogWidget(widget_id=widget_id, position=position, trigger=trigger, max_items=max_items, theme=theme)
        self._widgets[installation_id] = w
        return w

    def record_impression(self, installation_id: str) -> ChangelogWidget:
        w = self._get(installation_id)
        w.impressions += 1
        return w

    def record_click(self, installation_id: str) -> ChangelogWidget:
        w = self._get(installation_id)
        w.clicks += 1
        return w

    def get_widget(self, installation_id: str) -> ChangelogWidget:
        return self._get(installation_id)

    def _get(self, installation_id: str) -> ChangelogWidget:
        w = self._widgets.get(installation_id)
        if w is None: raise KeyError("Widget not configured")
        return w
