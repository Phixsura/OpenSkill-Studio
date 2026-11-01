"""Search page — full marketplace search results page."""

import html
from collections import defaultdict


def build_search_results_page(*, query: str, results: list[dict],
                                  sort_by: str = "relevance",
                                  category: str | None = None) -> dict:
    filtered = results
    if category:
        filtered = [r for r in filtered if r.get("category") == category]
    if sort_by == "downloads":
        filtered = sorted(filtered, key=lambda r: r.get("downloads", 0), reverse=True)
    elif sort_by == "rating":
        filtered = sorted(filtered, key=lambda r: r.get("rating", 0), reverse=True)
    items = [{
        "id": r.get("id", ""), "name": html.escape(r.get("name", "")),
        "icon": r.get("icon", "📦"), "tagline": html.escape(r.get("tagline", "")),
        "category": r.get("category", ""), "rating": r.get("rating", 0),
        "downloads": r.get("downloads", 0), "verified": r.get("verified", False),
    } for r in filtered]
    cat_counts: dict[str, int] = defaultdict(int)
    for r in results:
        cat_counts[r.get("category", "")] += 1
    return {
        "query": query, "results": items, "total": len(items),
        "sort_by": sort_by, "category_filter": category,
        "categories": dict(cat_counts),
        "has_results": len(items) > 0,
    }
