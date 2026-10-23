"""Search history — track and manage user search history."""


def add_to_history(*, history: list[str], query: str, max_items: int = 20) -> list[str]:
    # Remove if exists, add to front
    filtered = [q for q in history if q.lower() != query.lower()]
    return [query] + filtered[:max_items - 1]


def clear_history() -> list[str]:
    return []


def get_recent_searches(*, history: list[str], limit: int = 5) -> list[str]:
    return history[:limit]


def get_search_analytics(*, searches: list[dict]) -> dict:
    if not searches:
        return {"total": 0, "unique": 0, "avg_results": 0, "zero_results_pct": 0}
    unique = len(set(s.get("query", "").lower() for s in searches))
    total_results = sum(s.get("results_count", 0) for s in searches)
    zero = sum(1 for s in searches if s.get("results_count", 0) == 0)
    return {"total": len(searches), "unique": unique,
            "avg_results": round(total_results / len(searches), 1),
            "zero_results_pct": round(zero / len(searches) * 100, 1)}
