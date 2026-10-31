"""App recommendation engine — personalized app suggestions based on usage."""
from __future__ import annotations
import math


def recommend_apps(*, user_apps: list[str], user_categories: list[str],
                     all_apps: list[dict], limit: int = 6) -> list[dict]:
    scored = []
    for app in all_apps:
        if app["id"] in user_apps:
            continue
        score = 0
        if app.get("category") in user_categories:
            score += 5
        score += math.log10(max(app.get("installs", 1), 1)) * 2
        score += app.get("rating", 0) * 3
        if app.get("verified"):
            score += 2
        scored.append({**app, "recommendation_score": round(score, 1)})
    scored.sort(key=lambda x: -x["recommendation_score"])
    return scored[:limit]


def get_because_you_use(*, installed_app: dict, all_apps: list[dict],
                          limit: int = 4) -> list[dict]:
    category = installed_app.get("category", "")
    similar = [a for a in all_apps if a.get("category") == category
               and a.get("id") != installed_app.get("id")]
    similar.sort(key=lambda a: -a.get("rating", 0))
    return [{"id": a["id"], "name": a.get("name", ""), "icon": a.get("icon", "📱"),
             "rating": a.get("rating", 0), "reason": f"Similar to {installed_app.get('name', '')}"}
            for a in similar[:limit]]
