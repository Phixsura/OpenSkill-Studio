"""Marketplace search — full marketplace search with facets and sorting."""

import html
from collections import defaultdict


def search_marketplace(*, query: str, apps: list[dict], category: str | None = None,
                         sort_by: str = "relevance", limit: int = 20) -> dict:
    q = query.lower().strip()
    results = []
    for app in apps:
        name = app.get("name", "").lower()
        desc = app.get("description", "").lower()
        tags = " ".join(app.get("tags", [])).lower()
        if category and app.get("category") != category:
            continue
        score = 0
        if q in name:
            score += 10
        if q in desc:
            score += 5
        if q in tags:
            score += 3
        if score > 0 or not q:
            results.append({**app, "name": html.escape(app.get("name", "")),
                            "description": html.escape(app.get("description", "")[:100]),
                            "_score": score})
    if sort_by == "relevance":
        results.sort(key=lambda x: -x["_score"])
    elif sort_by == "downloads":
        results.sort(key=lambda x: -x.get("downloads", 0))
    elif sort_by == "rating":
        results.sort(key=lambda x: -x.get("rating", 0))
    elif sort_by == "newest":
        results.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    page = results[:limit]
    cat_counts: dict[str, int] = defaultdict(int)
    for r in results:
        cat_counts[r.get("category", "")] += 1
    return {"results": page, "total": len(results), "query": query,
            "sort_by": sort_by, "facets": {"category": dict(cat_counts)}}
