"""Marketplace search v2 — advanced search with facets, sorting, and pagination."""


def search_v2(*, query: str, apps: list[dict], filters: dict | None = None,
                sort_by: str = "relevance", page: int = 1, per_page: int = 20) -> dict:
    q = query.lower()
    results = []
    for app in apps:
        score = 0
        name = app.get("name", "").lower()
        if q == name: score = 100
        elif name.startswith(q): score = 80
        elif q in name: score = 60
        elif q in app.get("description", "").lower(): score = 30
        if score > 0:
            results.append({**app, "_score": score})

    # Apply filters
    if filters:
        if filters.get("category"):
            results = [r for r in results if r.get("category") == filters["category"]]
        if filters.get("min_rating"):
            results = [r for r in results if r.get("avg_rating", 0) >= filters["min_rating"]]
        if filters.get("free_only"):
            results = [r for r in results if r.get("price_cents", 0) == 0]

    # Sort
    if sort_by == "relevance":
        results.sort(key=lambda r: -r["_score"])
    elif sort_by == "installs":
        results.sort(key=lambda r: -r.get("install_count", 0))
    elif sort_by == "rating":
        results.sort(key=lambda r: -r.get("avg_rating", 0))
    elif sort_by == "newest":
        results.sort(key=lambda r: r.get("created_at", ""), reverse=True)

    total = len(results)
    start = (page - 1) * per_page
    page_results = results[start:start + per_page]

    # Build facets
    cats: dict[str, int] = {}
    for r in results:
        c = r.get("category", "other")
        cats[c] = cats.get(c, 0) + 1

    return {"results": page_results, "total": total, "page": page, "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
            "facets": {"categories": cats}, "query": query, "sort": sort_by}
