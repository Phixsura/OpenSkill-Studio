"""Analytics Overview — top-level analytics for the entire platform.

The grand analytics service: DAU/WAU/MAU, revenue trends, extension
growth, developer acquisition, and platform engagement metrics.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PlatformAnalytics:
    dau: int = 0
    wau: int = 0
    mau: int = 0
    extensions_published_today: int = 0
    installs_today: int = 0
    revenue_today_cents: int = 0
    api_calls_today: int = 0
    new_developers_today: int = 0
    avg_session_minutes: float = 0.0
    retention_7d: float = 0.0
    nps_score: float = 0.0


class PlatformAnalyticsOverviewService:
    """Top-level platform analytics."""

    def __init__(self):
        self._analytics = PlatformAnalytics()

    def update(self, **kwargs) -> PlatformAnalytics:
        for k, v in kwargs.items():
            if hasattr(self._analytics, k):
                setattr(self._analytics, k, v)
        return self._analytics

    def get_overview(self) -> dict:
        a = self._analytics
        return {
            "engagement": {"dau": a.dau, "wau": a.wau, "mau": a.mau,
                           "dau_wau_ratio": round(a.dau / max(a.wau, 1) * 100, 1),
                           "avg_session": a.avg_session_minutes,
                           "retention_7d": a.retention_7d},
            "growth": {"extensions_today": a.extensions_published_today,
                       "installs_today": a.installs_today,
                       "new_devs_today": a.new_developers_today},
            "revenue": {"today_cents": a.revenue_today_cents,
                        "projected_monthly": a.revenue_today_cents * 30},
            "api": {"calls_today": a.api_calls_today},
            "satisfaction": {"nps": a.nps_score},
        }

    def get_health_indicators(self) -> list[dict]:
        a = self._analytics
        indicators = []
        dau_wau = a.dau / max(a.wau, 1) * 100
        if dau_wau >= 40:
            indicators.append({"metric": "Engagement", "status": "excellent", "value": f"{dau_wau:.0f}% DAU/WAU"})
        elif dau_wau >= 20:
            indicators.append({"metric": "Engagement", "status": "good", "value": f"{dau_wau:.0f}% DAU/WAU"})
        else:
            indicators.append({"metric": "Engagement", "status": "needs_work", "value": f"{dau_wau:.0f}% DAU/WAU"})

        if a.retention_7d >= 40:
            indicators.append({"metric": "Retention", "status": "excellent", "value": f"{a.retention_7d}%"})
        else:
            indicators.append({"metric": "Retention", "status": "needs_work", "value": f"{a.retention_7d}%"})

        if a.nps_score >= 50:
            indicators.append({"metric": "NPS", "status": "excellent", "value": str(a.nps_score)})
        elif a.nps_score >= 0:
            indicators.append({"metric": "NPS", "status": "good", "value": str(a.nps_score)})

        return indicators
