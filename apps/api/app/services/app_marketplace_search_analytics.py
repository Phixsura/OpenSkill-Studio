"""Marketplace search analytics — track what users search for."""

from collections import defaultdict

_searches: list[dict] = []
_term_counts: dict[str, int] = defaultdict(int)


def record_search(*, query: str, results_count: int, user_id: str | None = None) -> None:
    from datetime import UTC, datetime
    _searches.append({"query": query, "results_count": results_count, "user_id": user_id, "timestamp": datetime.now(UTC).isoformat()})
    for term in query.lower().split():
        _term_counts[term] += 1


def get_top_searches(*, limit: int = 20) -> list[dict]:
    return [{"term": t, "count": c} for t, c in sorted(_term_counts.items(), key=lambda x: x[1], reverse=True)[:limit]]


def get_zero_result_queries(*, limit: int = 20) -> list[str]:
    zero = [s["query"] for s in _searches if s["results_count"] == 0]
    counts = defaultdict(int)
    for q in zero:
        counts[q] += 1
    return [q for q, _ in sorted(counts.items(), key=lambda x: x[1], reverse=True)[:limit]]
