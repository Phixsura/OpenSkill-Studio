"""Marketplace search — full-featured search with filters and facets."""


def search_marketplace(*, query: str, apps: list[dict], filters: dict | None = None,
                          sort: str = "relevance", page: int = 1, per_page: int = 20) -> dict:
    q = query.lower().strip()
    results = []
    for app in apps:
        score = 0
        name = app.get("name", "").lower()
        desc = app.get("description", "").lower()
        if q in name:
            score += 10
        if name.startswith(q):
            score += 5
        if q in desc:
            score += 3
        if score > 0:
            results.append({**app, "_score": score})
    # Apply filters
    if filters:
        if filters.get("category"):
            results = [r for r in results if r.get("category") == filters["category"]]
        if filters.get("min_rating"):
            results = [r for r in results if r.get("rating", 0) >= filters["min_rating"]]
        if filters.get("free_only"):
            results = [r for r in results if r.get("price", 0) == 0]
    # Sort
    if sort == "rating":
        results.sort(key=lambda r: r.get("rating", 0), reverse=True)
    elif sort == "installs":
        results.sort(key=lambda r: r.get("installs", 0), reverse=True)
    else:
        results.sort(key=lambda r: r.get("_score", 0), reverse=True)
    # Paginate
    total = len(results)
    start = (page - 1) * per_page
    page_results = results[start:start + per_page]
    # Clean scores
    for r in page_results:
        r.pop("_score", None)
    # Facets
    cat_counts: dict[str, int] = {}
    for r in results:
        cat = r.get("category", "other")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    return {
        "results": page_results,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": max((total + per_page - 1) // per_page, 1),
        "query": query,
        "facets": {"categories": cat_counts},
    }
