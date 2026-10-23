"""App marketplace search bar — search with recent and popular suggestions."""

import html

POPULAR_SEARCHES = ["code editor", "slack integration", "analytics", "deploy", "webhook",
                     "authentication", "monitoring", "testing"]


def build_search_suggestions(*, query: str, recent_searches: list[str] | None = None,
                                popular: list[str] | None = None) -> dict:
    q = query.lower().strip()
    pops = popular or POPULAR_SEARCHES
    matched = [p for p in pops if q in p][:5] if q else []
    recent = [html.escape(r) for r in (recent_searches or [])[:5]]
    return {
        "query": query,
        "matched_popular": matched,
        "recent_searches": recent,
        "show_popular": not q,
        "show_matched": len(matched) > 0,
        "popular_searches": pops[:8],
    }
