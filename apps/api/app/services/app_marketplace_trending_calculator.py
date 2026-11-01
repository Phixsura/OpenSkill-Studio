"""Marketplace trending calculator — compute trending score with time decay."""

import math
from datetime import UTC, datetime, timedelta


def compute_trending_with_decay(*, installs_7d: int, executions_7d: int, reviews_7d: int,
                                   health_score: int, days_since_publish: int) -> float:
    """Trending score with exponential time decay (half-life 14 days)."""
    activity = installs_7d * 3 + executions_7d * 0.05 + reviews_7d * 5
    health_bonus = health_score / 100
    decay = math.exp(-0.693 * max(days_since_publish - 7, 0) / 14)
    return round(activity * health_bonus * decay, 2)


def rank_trending_apps(apps: list[dict], *, limit: int = 10) -> list[dict]:
    for app in apps:
        app["_trend_score"] = compute_trending_with_decay(
            installs_7d=app.get("installs_7d", 0), executions_7d=app.get("executions_7d", 0),
            reviews_7d=app.get("reviews_7d", 0), health_score=app.get("health_score", 100),
            days_since_publish=app.get("days_since_publish", 0))
    return sorted(apps, key=lambda a: a["_trend_score"], reverse=True)[:limit]
