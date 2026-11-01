"""Search suggest — autocomplete and search suggestions."""


def get_suggestions(*, query: str, catalog: list[dict], limit: int = 5) -> dict:
    if not query or len(query) < 2:
        return {"suggestions": [], "query": query}
    q = query.lower()
    scored = []
    for item in catalog:
        name = item.get("name", "").lower()
        category = item.get("category", "").lower()
        if name.startswith(q):
            scored.append({"text": item["name"], "type": "app", "id": item["id"], "score": 100})
        elif q in name:
            scored.append({"text": item["name"], "type": "app", "id": item["id"], "score": 50})
        elif q in category:
            scored.append({"text": item["name"], "type": "category_match", "id": item["id"], "score": 30})
    scored.sort(key=lambda x: x["score"], reverse=True)
    return {"suggestions": scored[:limit], "query": query, "total": len(scored)}


def get_trending_searches(*, recent_queries: list[str], limit: int = 5) -> dict:
    counts: dict[str, int] = {}
    for q in recent_queries:
        key = q.lower().strip()
        if key:
            counts[key] = counts.get(key, 0) + 1
    sorted_q = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return {"trending": [{"query": q, "count": c} for q, c in sorted_q[:limit]]}
