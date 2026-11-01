"""Smart recommendation — personalized app suggestions."""

import hashlib


def recommend_apps(*, user_id: str, installed_apps: list[str],
                     catalog: list[dict], limit: int = 5) -> dict:
    installed_set = set(installed_apps)
    candidates = [app for app in catalog if app["id"] not in installed_set]
    scored = []
    for app in candidates:
        score = app.get("rating", 3.0) * 20
        score += min(app.get("install_count", 0) / 100, 50)
        # category affinity: boost if user has apps in same category
        installed_cats = {a.get("category") for a in catalog if a["id"] in installed_set}
        if app.get("category") in installed_cats:
            score += 30
        # deterministic user-app hash for variety
        h = int(hashlib.sha256(f"{user_id}:{app['id']}".encode()).hexdigest(), 16) % 20
        score += h
        scored.append({**app, "_score": round(score, 1)})
    scored.sort(key=lambda x: x["_score"], reverse=True)
    results = [{"id": a["id"], "name": a["name"], "category": a.get("category"),
                "rating": a.get("rating"), "score": a["_score"],
                "reason": "category_match" if a.get("category") in installed_cats else "popular"}
               for a in scored[:limit]]
    return {"user_id": user_id, "recommendations": results,
            "total_candidates": len(candidates)}
