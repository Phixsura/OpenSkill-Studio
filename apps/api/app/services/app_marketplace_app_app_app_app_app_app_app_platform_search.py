"""Platform-wide search — search across all platform entities."""
from __future__ import annotations


ENTITY_TYPES = ["service", "deployment", "incident", "runbook", "config", "user", "team"]


def search_platform(query: str, entities: list[dict], limit: int = 20) -> dict:
    q = query.lower()
    results = []
    for e in entities:
        name = str(e.get("name", "")).lower()
        desc = str(e.get("description", "")).lower()
        etype = e.get("type", "")
        if q in name:
            results.append({**e, "match_field": "name", "score": 1.0})
        elif q in desc:
            results.append({**e, "match_field": "description", "score": 0.5})
    results.sort(key=lambda r: -r["score"])
    by_type: dict[str, int] = {}
    for r in results:
        by_type[r.get("type", "")] = by_type.get(r.get("type", ""), 0) + 1
    return {"results": results[:limit], "total_matches": len(results),
            "by_type": by_type, "query": query}
