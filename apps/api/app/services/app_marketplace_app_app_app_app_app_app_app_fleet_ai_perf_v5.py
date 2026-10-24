"""Fleet AI Performance v5 — track ultimate platform performance."""
from __future__ import annotations
def fleet_ai_performance_v5(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    p50 = round(sum(m.get("p50_ms", 0) for m in monitors) / max(len(monitors), 1), 1)
    p99 = round(sum(m.get("p99_ms", 0) for m in monitors) / max(len(monitors), 1), 1)
    throughput = sum(m.get("rps", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "p50_ms": p50,
            "p99_ms": p99, "rps": throughput, "fast": p99 < 100}
