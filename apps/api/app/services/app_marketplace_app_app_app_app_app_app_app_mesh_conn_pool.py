"""Mesh connection pool monitor — monitor connection pools in the mesh."""
from __future__ import annotations


def monitor_pools(pools: list[dict]) -> dict:
    results = []
    saturated = 0
    for p in pools:
        active = p.get("active", 0)
        max_size = p.get("max_size", 100)
        util = round(active / max(max_size, 1) * 100, 1)
        is_saturated = util >= 90
        if is_saturated:
            saturated += 1
        results.append({"service": p["service"], "destination": p.get("destination", ""),
                        "active": active, "max_size": max_size, "util_pct": util,
                        "saturated": is_saturated})
    return {"pools": results, "total": len(results), "saturated": saturated,
            "healthy": len(results) - saturated}


def pool_recommendation(pool: dict) -> dict:
    util = pool.get("util_pct", 0)
    if util >= 90:
        return {"action": "increase_pool_size", "urgency": "high"}
    elif util >= 70:
        return {"action": "monitor", "urgency": "medium"}
    elif util < 20:
        return {"action": "decrease_pool_size", "urgency": "low"}
    return {"action": "no_change", "urgency": "none"}
