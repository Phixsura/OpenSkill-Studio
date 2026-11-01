"""App discovery — personalized app recommendations."""

import html
from collections import defaultdict


def recommend_apps(*, user_interests: list[str], installed_apps: list[str],
                     catalog: list[dict], limit: int = 8) -> dict:
    installed = set(installed_apps)
    scored = []
    for app in catalog:
        if app.get("id") in installed:
            continue
        tags = set(app.get("tags", []))
        cat = app.get("category", "")
        score = len(tags & set(user_interests)) * 3
        if cat in user_interests:
            score += 5
        if score > 0: score += app.get("rating", 0)
        if score > 0:
            scored.append({
                "id": app["id"], "name": html.escape(app.get("name", "")),
                "icon": app.get("icon", "📦"), "category": cat,
                "rating": app.get("rating", 0), "score": round(score, 1),
                "reason": "Based on your interests",
            })
    scored.sort(key=lambda x: -x["score"])
    return {"recommendations": scored[:limit], "total_found": len(scored),
            "based_on": user_interests}
