"""App API Developer Changelog Analytics — engagement analytics for changelogs."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogAnalytics:
    total_views: int = 0
    unique_viewers: int = 0
    total_reactions: int = 0
    total_comments: int = 0
    total_bookmarks: int = 0
    avg_time_on_page_seconds: float = 0.0
    most_viewed_version: str = ""
    most_reacted_version: str = ""

    @property
    def engagement_rate(self) -> float:
        if self.total_views == 0: return 0.0
        return round((self.total_reactions + self.total_comments + self.total_bookmarks) / self.total_views * 100, 1)

class AppAPIDeveloperChangelogAnalytics:
    def __init__(self) -> None:
        self._analytics: dict[str, ChangelogAnalytics] = {}

    def update(self, installation_id: str, **kwargs) -> ChangelogAnalytics:
        if not installation_id: raise ValueError("installation_id is required")
        if installation_id not in self._analytics:
            self._analytics[installation_id] = ChangelogAnalytics()
        a = self._analytics[installation_id]
        for k, v in kwargs.items():
            if hasattr(a, k): setattr(a, k, v)
        return a

    def get(self, installation_id: str) -> ChangelogAnalytics:
        return self._analytics.get(installation_id, ChangelogAnalytics())
