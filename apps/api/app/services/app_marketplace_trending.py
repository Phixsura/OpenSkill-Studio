"""Marketplace trending — compute trending apps based on recent activity."""

from datetime import UTC, datetime, timedelta


def compute_trending_score(*, recent_installs: int, recent_executions: int, recent_reviews: int,
                           days: int = 7) -> float:
    """Compute trending score — weighted recent activity."""
    return round(recent_installs * 3.0 + recent_executions * 0.1 + recent_reviews * 5.0, 2)


def rank_trending(apps: list[dict], *, limit: int = 10) -> list[dict]:
    """Rank apps by trending score."""
    for app in apps:
        app["_trending_score"] = compute_trending_score(
            recent_installs=app.get("recent_installs", 0),
            recent_executions=app.get("recent_executions", 0),
            recent_reviews=app.get("recent_reviews", 0),
        )
    ranked = sorted(apps, key=lambda a: a["_trending_score"], reverse=True)
    return ranked[:limit]
