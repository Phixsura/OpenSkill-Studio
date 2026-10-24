"""Search suggestions — typeahead suggestions for marketplace search."""

from collections import defaultdict


def get_suggestions(*, query: str, apps: list[dict], categories: list[str],
                      recent_searches: list[str], limit: int = 8) -> dict:
    q = query.lower()
    if len(q) < 2:
        return {"suggestions": [], "recent": recent_searches[:3]}

    results = []
    # App name matches
    for app in apps:
        name = app.get("name", "").lower()
        if name.startswith(q):
            results.append({"type": "app", "text": app["name"], "id": app.get("id"), "icon": "📦"})
        elif q in name:
            results.append({"type": "app", "text": app["name"], "id": app.get("id"), "icon": "📦"})
    # Category matches
    for cat in categories:
        if q in cat.lower():
            results.append({"type": "category", "text": cat, "icon": "📂"})
    # Recent search matches
    for rs in recent_searches:
        if q in rs.lower() and not any(r["text"] == rs for r in results):
            results.append({"type": "recent", "text": rs, "icon": "🕐"})

    return {"suggestions": results[:limit], "total": len(results), "query": query}


def track_search(*, query: str, results_count: int, clicked_result: str | None = None) -> dict:
    return {"query": query, "results_count": results_count, "clicked": clicked_result,
            "has_results": results_count > 0, "converted": clicked_result is not None}


def get_popular_searches(*, search_logs: list[dict], limit: int = 10) -> list[dict]:
    counts = defaultdict(int)
    for log in search_logs:
        counts[log.get("query", "")] += 1
    return [{"query": q, "count": c} for q, c in sorted(counts.items(), key=lambda x: -x[1])[:limit]]
