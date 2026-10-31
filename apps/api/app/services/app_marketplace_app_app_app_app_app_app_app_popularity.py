"""App popularity tracker — compute and rank app popularity scores."""
from __future__ import annotations
import math


def compute_popularity(*, installs_30d: int, reviews_30d: int, api_calls_30d: int,
                         active_users: int, rating: float) -> dict:
    install_score = math.log10(max(installs_30d, 1)) * 3
    review_score = math.log10(max(reviews_30d, 1)) * 2
    usage_score = math.log10(max(api_calls_30d, 1)) * 1.5
    engagement = math.log10(max(active_users, 1)) * 2
    quality = rating * 4
    total = round(install_score + review_score + usage_score + engagement + quality, 1)
    tier = "platinum" if total >= 40 else "gold" if total >= 30 else "silver" if total >= 20 else "bronze"
    return {"score": total, "tier": tier,
            "breakdown": {"installs": round(install_score, 1), "reviews": round(review_score, 1),
                           "usage": round(usage_score, 1), "engagement": round(engagement, 1),
                           "quality": round(quality, 1)}}


def rank_apps_by_popularity(apps: list[dict], *, limit: int = 10) -> list[dict]:
    scored = []
    for a in apps:
        pop = compute_popularity(**{k: a.get(k, 0) for k in
              ["installs_30d", "reviews_30d", "api_calls_30d", "active_users", "rating"]})
        scored.append({"name": a.get("name", ""), "icon": a.get("icon", "📱"),
                        "score": pop["score"], "tier": pop["tier"]})
    scored.sort(key=lambda x: -x["score"])
    for i, s in enumerate(scored[:limit]):
        s["rank"] = i + 1
    return scored[:limit]
