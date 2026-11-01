"""Fleet AI Performance v7 — track ultimate platform performance."""
from __future__ import annotations
def fleet_ai_performance_v7_final(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    p50 = round(sum(m.get("p50_ms", 0) for m in monitors) / max(len(monitors), 1), 1)
    p99 = round(sum(m.get("p99_ms", 0) for m in monitors) / max(len(monitors), 1), 1)
    throughput = sum(m.get("rps", 0) for m in monitors)
    efficiency = round(sum(m.get("eff_pct", 0) for m in monitors) / max(len(monitors), 1), 1)
    return {"monitors": len(monitors), "active": len(active), "p50": p50, "p99": p99,
            "throughput": throughput, "efficiency": efficiency, "blazing": p99 < 50}
