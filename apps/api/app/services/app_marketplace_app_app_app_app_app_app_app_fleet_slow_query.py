"""Fleet slow query — detect slow database queries."""
from __future__ import annotations
def fleet_slow_queries(queries: list[dict]) -> dict:
    slow = [q for q in queries if q.get("duration_ms", 0) > 1000]
    very_slow = [q for q in queries if q.get("duration_ms", 0) > 5000]
    return {"total": len(queries), "slow": len(slow), "very_slow": len(very_slow),
            "needs_attention": len(very_slow) > 0}
