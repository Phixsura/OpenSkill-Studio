"""API throughput planner — plan capacity based on throughput requirements."""
from __future__ import annotations
import math


def plan_throughput(target_rps: int, avg_latency_ms: float, max_concurrent: int) -> dict:
    concurrent_needed = math.ceil(target_rps * avg_latency_ms / 1000)
    instances = math.ceil(concurrent_needed / max(max_concurrent, 1))
    headroom = round(instances * max_concurrent / max(concurrent_needed, 1) * 100 - 100, 1)
    return {"target_rps": target_rps, "concurrent_needed": concurrent_needed,
            "instances_needed": instances, "headroom_pct": headroom,
            "max_concurrent_per_instance": max_concurrent}


def growth_plan(current_rps: int, growth_rate_pct: float, months: int = 6,
                avg_latency_ms: float = 50, max_concurrent: int = 100) -> list[dict]:
    plan = []
    rps = current_rps
    for m in range(1, months + 1):
        rps = round(rps * (1 + growth_rate_pct / 100))
        p = plan_throughput(rps, avg_latency_ms, max_concurrent)
        plan.append({"month": m, "rps": rps, "instances": p["instances_needed"]})
    return plan
