"""Database query profiler — analyze slow queries and suggest optimizations."""
from __future__ import annotations


def profile_queries(queries: list[dict]) -> dict:
    slow = [q for q in queries if q.get("duration_ms", 0) >= 100]
    very_slow = [q for q in queries if q.get("duration_ms", 0) >= 1000]
    no_index = [q for q in queries if not q.get("uses_index", True)]
    full_scans = [q for q in queries if q.get("scan_type") == "full"]
    total_time = sum(q.get("duration_ms", 0) for q in queries)
    avg_time = round(total_time / max(len(queries), 1), 1)
    results = sorted(queries, key=lambda q: -q.get("duration_ms", 0))
    suggestions = []
    for q in no_index:
        suggestions.append({"query": q.get("query", "")[:80], "suggestion": "Add index",
                             "impact": "high"})
    for q in full_scans:
        suggestions.append({"query": q.get("query", "")[:80], "suggestion": "Avoid full table scan",
                             "impact": "high"})
    return {
        "total_queries": len(queries), "slow_queries": len(slow),
        "very_slow": len(very_slow), "no_index": len(no_index),
        "full_scans": len(full_scans), "total_time_ms": total_time,
        "avg_time_ms": avg_time, "suggestions": suggestions,
        "top_slow": [{"query": q.get("query", "")[:100], "duration_ms": q["duration_ms"],
                       "table": q.get("table", "")} for q in results[:5]],
    }
