"""Fleet GraphQL metrics — track GraphQL query performance."""
from __future__ import annotations
def fleet_graphql_metrics(queries: list[dict]) -> dict:
    total = len(queries)
    slow = [q for q in queries if q.get("duration_ms", 0) > 1000]
    deep = [q for q in queries if q.get("depth", 0) > 5]
    avg_dur = round(sum(q.get("duration_ms", 0) for q in queries) / max(total, 1), 1)
    return {"total": total, "slow_queries": len(slow), "deep_queries": len(deep),
            "avg_duration_ms": avg_dur, "healthy": len(slow) == 0}
