"""Fleet AI Warm Pool — track pre-initialized inference instances."""
from __future__ import annotations
def fleet_ai_warm_pool(pools: list[dict]) -> dict:
    active = [p for p in pools if p.get("active", True)]
    warm_instances = sum(p.get("warm", 0) for p in pools)
    cold_starts_prevented = sum(p.get("prevented", 0) for p in pools)
    cost_overhead_pct = round(sum(p.get("overhead_pct", 0) for p in pools) / max(len(pools), 1), 1)
    return {"pools": len(pools), "active": len(active), "warm": warm_instances,
            "prevented": cold_starts_prevented, "overhead_pct": cost_overhead_pct, "ready": warm_instances > 0}
