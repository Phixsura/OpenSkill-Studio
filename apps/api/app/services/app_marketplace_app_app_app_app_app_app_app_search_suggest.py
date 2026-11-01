"""Search suggestions — provide search suggestions based on popular queries."""
from __future__ import annotations

POPULAR_SEARCHES = [
    "slack integration", "github sync", "analytics dashboard", "webhook manager",
    "sso provider", "payment gateway", "email notifications", "monitoring alerts",
    "deployment automation", "api testing", "code review", "ci/cd pipeline",
]


def get_suggestions(prefix: str, *, limit: int = 5) -> list[str]:
    p = prefix.lower().strip()
    if not p:
        return POPULAR_SEARCHES[:limit]
    return [s for s in POPULAR_SEARCHES if s.startswith(p)][:limit]


def get_trending_searches(*, limit: int = 6) -> list[dict]:
    return [{"query": q, "trend": "🔥"} for q in POPULAR_SEARCHES[:limit]]


def build_search_page(query: str) -> dict:
    suggestions = get_suggestions(query)
    return {"query": query, "suggestions": suggestions,
            "suggestion_count": len(suggestions),
            "show_trending": not query}
