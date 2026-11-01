"""Developer Analytics — aggregate analytics across all developer's extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class DevAnalytics:
    developer_id: str
    total_extensions: int = 0
    total_installs: int = 0
    total_reviews: int = 0
    avg_rating: float = 0.0
    total_revenue_cents: int = 0
    active_users_30d: int = 0
    top_extension: str = ""


class ExtDevAnalyticsService:
    def __init__(self):
        self._analytics: dict[str, DevAnalytics] = {}

    def update(self, developer_id: str, **kwargs) -> DevAnalytics:
        if developer_id not in self._analytics:
            self._analytics[developer_id] = DevAnalytics(developer_id=developer_id)
        a = self._analytics[developer_id]
        for k, v in kwargs.items():
            if hasattr(a, k):
                setattr(a, k, v)
        return a

    def get(self, developer_id: str) -> DevAnalytics | None:
        return self._analytics.get(developer_id)

    def get_leaderboard(self, metric: str = "total_installs", limit: int = 10) -> list[DevAnalytics]:
        all_devs = list(self._analytics.values())
        return sorted(all_devs, key=lambda a: getattr(a, metric, 0), reverse=True)[:limit]

    def get_growth(self, developer_id: str) -> dict:
        a = self._analytics.get(developer_id)
        if not a: return {}
        revenue_per_install = (a.total_revenue_cents / a.total_installs) if a.total_installs > 0 else 0
        reviews_per_install = (a.total_reviews / a.total_installs * 100) if a.total_installs > 0 else 0
        return {
            "revenue_per_install_cents": round(revenue_per_install),
            "review_rate_pct": round(reviews_per_install, 1),
            "extensions": a.total_extensions,
        }
