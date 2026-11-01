"""Search results page builder — compile search results page data."""


def build_search_results_page(*, query: str, results: list[dict], total: int,
                                 page: int, per_page: int, filters: dict) -> dict:
    return {
        "query": query,
        "results": results,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": (total + per_page - 1) // per_page if per_page > 0 else 1,
        "has_results": total > 0,
        "filters": filters,
        "suggestion": f"Try searching for '{query.split()[0]}'" if query and " " in query and total == 0 else None,
    }
