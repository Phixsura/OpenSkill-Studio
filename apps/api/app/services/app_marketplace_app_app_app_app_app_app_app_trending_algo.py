"""Trending algorithm — compute trending apps based on recent activity."""
from __future__ import annotations
import math


def compute_trending_score(*, recent_installs: int, recent_reviews: int,
                              recent_api_calls: int, rating: float,
                              days_since_update: int) -> float:
    install_score = math.log10(max(recent_installs, 1)) * 3
    review_score = math.log10(max(recent_reviews, 1)) * 2
    api_score = math.log10(max(recent_api_calls, 1)) * 1
    quality_bonus = rating * 2
    freshness = max(0, 10 - days_since_update * 0.5)
    return round(install_score + review_score + api_score + quality_bonus + freshness, 2)


def rank_trending(apps: list[dict], *, limit: int = 20) -> list[dict]:
    scored = []
    for a in apps:
        score = compute_trending_score(
            recent_installs=a.get("recent_installs", 0),
            recent_reviews=a.get("recent_reviews", 0),
            recent_api_calls=a.get("recent_api_calls", 0),
            rating=a.get("rating", 0),
            days_since_update=a.get("days_since_update", 30))
        scored.append({**a, "trending_score": score})
    scored.sort(key=lambda x: -x["trending_score"])
    for i, s in enumerate(scored[:limit]):
        s["rank"] = i + 1
    return scored[:limit]
