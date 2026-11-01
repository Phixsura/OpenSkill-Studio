"""Empty search — helpful empty search state with suggestions."""


def build_empty_search(*, query: str, suggestions: list[str] | None = None) -> dict:
    default_suggestions = ["Try broader keywords", "Check for typos",
                            "Browse categories instead", "Use fewer filters"]
    popular = ["auth", "analytics", "payments", "charts", "notifications"]
    return {
        "query": query,
        "title": f'No results for "{query}"',
        "icon": "🔍",
        "suggestions": suggestions or default_suggestions,
        "popular_searches": popular,
        "has_suggestions": True,
    }
