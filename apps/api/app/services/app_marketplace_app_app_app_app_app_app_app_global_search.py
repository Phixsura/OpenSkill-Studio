"""Global search — unified search across all platform entities."""
from __future__ import annotations


ENTITY_TYPES = {"app", "user", "team", "webhook", "deployment", "document"}


def search_all(query: str, entities: list[dict], limit: int = 10) -> dict:
    q = query.lower()
    results = []
    by_type: dict[str, int] = {}
    for e in entities:
        name = e.get("name", "").lower()
        desc = e.get("description", "").lower()
        etype = e.get("type", "unknown")
        if q in name or q in desc:
            score = 1.0 if q in name else 0.5
            results.append({**e, "score": score, "match_field": "name" if q in name else "description"})
            by_type[etype] = by_type.get(etype, 0) + 1
    results.sort(key=lambda r: -r["score"])
    return {"results": results[:limit], "total_matches": len(results),
            "by_type": by_type, "query": query, "truncated": len(results) > limit}


def suggest_completions(query: str, names: list[str], limit: int = 5) -> list[str]:
    q = query.lower()
    matches = [n for n in names if n.lower().startswith(q)]
    contains = [n for n in names if q in n.lower() and not n.lower().startswith(q)]
    return (matches + contains)[:limit]
