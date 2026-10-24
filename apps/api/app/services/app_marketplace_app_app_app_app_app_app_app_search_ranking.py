"""Search ranking engine — rank marketplace apps by relevance, popularity, and quality."""
from __future__ import annotations
import math


def rank_apps(apps: list[dict], *, query: str, weights: dict | None = None) -> list[dict]:
    w = weights or {"relevance": 5.0, "popularity": 2.0, "quality": 3.0}
    q = query.lower()
    scored = []
    for app in apps:
        name = app.get("name", "").lower()
        desc = app.get("description", "").lower()
        # Relevance
        rel = 10 if q == name else 8 if name.startswith(q) else 5 if q in name else 2 if q in desc else 0
        if rel == 0:
            continue
        # Popularity
        installs = app.get("installs", 0)
        pop = min(10, math.log10(max(installs, 1)) * 2)
        # Quality
        rating = app.get("rating", 0)
        qual = rating * 2  # 0-10 scale
        score = round(rel * w["relevance"] + pop * w["popularity"] + qual * w["quality"], 2)
        scored.append({**app, "score": score, "relevance": rel, "popularity": round(pop, 1)})
    scored.sort(key=lambda x: -x["score"])
    return scored


def suggest_queries(prefix: str, app_names: list[str], *, limit: int = 5) -> list[str]:
    p = prefix.lower()
    return [n for n in app_names if n.lower().startswith(p)][:limit]
