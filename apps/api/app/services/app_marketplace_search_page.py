"""Search page — complete search results page with filters, facets, and pagination."""


def build_search_page(*, query: str, results: list[dict], total: int,
                         page: int, per_page: int, filters: dict,
                         facets: dict, suggestions: list[str]) -> dict:
    total_pages = max(1, (total + per_page - 1) // per_page)
    return {
        "page_type": "search_results",
        "query": query,
        "results": results,
        "pagination": {"page": page, "per_page": per_page, "total": total,
                         "total_pages": total_pages, "has_prev": page > 1,
                         "has_next": page < total_pages},
        "active_filters": filters,
        "facets": facets,
        "suggestions": suggestions[:5],
        "empty": total == 0,
        "seo": {"title": f'"{query}" — OpenSkill Marketplace Search',
                "description": f"Found {total} apps matching \"{query}\""},
    }


def build_zero_results_page(*, query: str, suggestions: list[str],
                               popular_apps: list[dict]) -> dict:
    return {
        "page_type": "zero_results",
        "query": query,
        "message": f'No apps found for "{query}"',
        "tips": [
            "Check your spelling",
            "Try more general keywords",
            "Browse categories instead",
        ],
        "did_you_mean": suggestions[:3],
        "popular_apps": popular_apps[:6],
    }
