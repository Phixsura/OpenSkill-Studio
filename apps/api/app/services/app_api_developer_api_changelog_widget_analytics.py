"""App API Developer API Changelog Widget Analytics — widget engagement metrics."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WidgetAnalytics:
    total_impressions: int = 0
    total_clicks: int = 0
    unique_viewers: int = 0
    entries_read: int = 0
    avg_time_on_widget_seconds: float = 0.0

    @property
    def ctr(self) -> float:
        if self.total_impressions == 0: return 0.0
        return round(self.total_clicks / self.total_impressions * 100, 1)

    @property
    def read_rate(self) -> float:
        if self.total_clicks == 0: return 0.0
        return round(self.entries_read / self.total_clicks * 100, 1)

class AppAPIDeveloperAPIChangelogWidgetAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, WidgetAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> WidgetAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._analytics:
            self._analytics[installation_id] = WidgetAnalytics()
        a = self._analytics[installation_id]
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        return a

    def get(self, installation_id: str) -> WidgetAnalytics:
        return self._analytics.get(installation_id, WidgetAnalytics())
