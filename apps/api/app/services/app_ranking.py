"""App marketplace ranking — score and rank apps for discovery.

Combines install count, health score, recency, and rating
into a composite ranking score for marketplace search results.
"""

import math
from datetime import UTC, datetime, timedelta


def compute_ranking_score(
    *,
    install_count: int = 0,
    health_score: int = 100,
    days_since_update: int = 0,
    rating: float = 0.0,
    rating_count: int = 0,
) -> float:
    """Compute a composite ranking score (0-100).

    Factors:
    - Install popularity (log scale, 30%)
    - Health score (20%)
    - Recency (exponential decay, 25%)
    - Rating (weighted by count, 25%)
    """
    # Popularity: log(installs + 1) normalized to ~0-1
    pop = min(math.log(install_count + 1) / math.log(10000), 1.0)

    # Health: 0-1
    health = health_score / 100.0

    # Recency: exponential decay, half-life = 90 days
    recency = math.exp(-0.693 * days_since_update / 90)

    # Rating: Bayesian average (min 5 ratings to count)
    if rating_count >= 5:
        rate = rating / 5.0  # Normalize to 0-1
    else:
        rate = 0.5  # Default to neutral

    score = (pop * 30 + health * 20 + recency * 25 + rate * 25)
    return round(score, 2)


def rank_apps(apps: list[dict]) -> list[dict]:
    """Rank a list of apps by composite score, descending."""
    for app in apps:
        app["_ranking_score"] = compute_ranking_score(
            install_count=app.get("install_count", 0),
            health_score=app.get("health_score", 100),
            days_since_update=app.get("days_since_update", 0),
            rating=app.get("rating", 0.0),
            rating_count=app.get("rating_count", 0),
        )
    return sorted(apps, key=lambda a: a["_ranking_score"], reverse=True)
