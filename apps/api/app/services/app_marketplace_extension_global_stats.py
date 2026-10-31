"""Global Stats — platform-wide statistics for the marketplace.

Aggregates total extensions, developers, installs, revenue, tests,
commits, and provides growth metrics.
"""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class PlatformGlobalStats:
    total_extensions: int
    total_developers: int
    total_installs: int
    total_revenue_cents: int
    total_api_calls: int
    total_services: int
    total_tests: int
    total_commits: int
    avg_rating: float
    uptime_percent: float


class ExtensionGlobalStatsService:
    """Aggregates and serves platform-wide statistics."""

    def __init__(self):
        self._stats = PlatformGlobalStats(
            total_extensions=0, total_developers=0, total_installs=0,
            total_revenue_cents=0, total_api_calls=0, total_services=0,
            total_tests=0, total_commits=0, avg_rating=0.0, uptime_percent=99.99,
        )

    def update(self, **kwargs: int | float) -> PlatformGlobalStats:
        for key, value in kwargs.items():
            if hasattr(self._stats, key):
                setattr(self._stats, key, value)
        return self._stats

    def increment(self, field: str, amount: int = 1) -> int:
        current = getattr(self._stats, field, 0)
        new_val = current + amount
        setattr(self._stats, field, new_val)
        return new_val

    def get_stats(self) -> dict:
        s = self._stats
        return {
            "extensions": s.total_extensions,
            "developers": s.total_developers,
            "installs": s.total_installs,
            "revenue": s.total_revenue_cents,
            "api_calls": s.total_api_calls,
            "services": s.total_services,
            "tests": s.total_tests,
            "commits": s.total_commits,
            "avg_rating": s.avg_rating,
            "uptime": s.uptime_percent,
        }

    def get_highlights(self) -> list[dict]:
        s = self._stats
        highlights = []
        if s.total_extensions >= 500:
            highlights.append({"metric": "extensions", "value": s.total_extensions, "label": "500+ Extensions"})
        if s.total_tests >= 2000:
            highlights.append({"metric": "tests", "value": s.total_tests, "label": "2000+ Tests GREEN"})
        if s.uptime_percent >= 99.9:
            highlights.append({"metric": "uptime", "value": s.uptime_percent, "label": "99.9%+ Uptime"})
        if s.total_commits >= 4000:
            highlights.append({"metric": "commits", "value": s.total_commits, "label": f"{s.total_commits}+ Commits"})
        return highlights
