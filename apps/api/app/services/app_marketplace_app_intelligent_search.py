"""Intelligent search — ranked search with typo tolerance and faceted results."""

import re
from collections import defaultdict


def search_apps(*, query: str, apps: list[dict], limit: int = 20) -> dict:
    if not query or len(query) < 2:
        return {"results": [], "total": 0, "facets": {}}
    q = query.lower()
    scored = []
    for app in apps:
        score = 0
        name = app.get("name", "").lower()
        desc = app.get("description", "").lower()
        if q == name:
            score = 100
        elif name.startswith(q):
            score = 80
        elif q in name:
            score = 60
        elif q in desc:
            score = 30
        elif _fuzzy_match(q, name):
            score = 20
        if score > 0:
            scored.append((score, app))
    scored.sort(key=lambda x: -x[0])
    results = [s[1] for s in scored[:limit]]
    facets = _build_facets(results)
    return {"results": results, "total": len(scored), "facets": facets}


def _fuzzy_match(query: str, target: str, max_distance: int = 2) -> bool:
    if abs(len(query) - len(target)) > max_distance:
        return False
    common = sum(1 for a, b in zip(query, target) if a == b)
    return common >= len(query) - max_distance


def _build_facets(apps: list[dict]) -> dict:
    cats = defaultdict(int)
    for a in apps:
        cats[a.get("category", "other")] += 1
    return {"categories": dict(sorted(cats.items(), key=lambda x: -x[1]))}
