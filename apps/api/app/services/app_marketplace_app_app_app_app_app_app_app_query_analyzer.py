"""Database query analyzer — analyze query performance."""
from __future__ import annotations


def analyze_query(query: str, execution_ms: float, rows_scanned: int,
                   rows_returned: int, index_used: bool) -> dict:
    efficiency = round(rows_returned / max(rows_scanned, 1) * 100, 1)
    slow = execution_ms > 100
    full_scan = not index_used and rows_scanned > 1000
    suggestions = []
    if full_scan:
        suggestions.append("Add index — full table scan detected")
    if efficiency < 10:
        suggestions.append(f"Low efficiency ({efficiency}%) — refine WHERE clause")
    if slow:
        suggestions.append(f"Slow query ({execution_ms}ms) — consider caching")
    return {"query_preview": query[:100], "execution_ms": execution_ms,
            "rows_scanned": rows_scanned, "rows_returned": rows_returned,
            "index_used": index_used, "efficiency_pct": efficiency,
            "slow": slow, "suggestions": suggestions}


def top_slow_queries(queries: list[dict], limit: int = 10) -> list[dict]:
    return sorted(queries, key=lambda q: -q.get("execution_ms", 0))[:limit]
