"""Global search — search across apps, docs, settings, and users."""


def global_search(*, query: str, catalogs: dict[str, list[dict]], limit: int = 10) -> dict:
    if not query or len(query) < 2:
        return {"results": [], "query": query, "total": 0}
    q = query.lower()
    results = []
    for category, items in catalogs.items():
        for item in items:
            searchable = " ".join(str(v) for v in item.values()).lower()
            if q in searchable:
                results.append({
                    "id": item.get("id", ""),
                    "title": item.get("title", item.get("name", "")),
                    "category": category,
                    "snippet": searchable[:100],
                })
    by_category: dict[str, int] = {}
    for r in results:
        by_category[r["category"]] = by_category.get(r["category"], 0) + 1
    return {
        "results": results[:limit],
        "total": len(results),
        "query": query,
        "by_category": by_category,
    }
