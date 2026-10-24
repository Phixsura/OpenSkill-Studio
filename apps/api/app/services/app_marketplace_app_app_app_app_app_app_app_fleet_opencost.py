"""Fleet OpenCost — track real-time k8s cost allocation."""
from __future__ import annotations
def fleet_opencost_status(namespaces: list[dict]) -> dict:
    total_daily = sum(n.get("daily_cost_usd", 0) for n in namespaces)
    idle_cost = sum(n.get("idle_cost_usd", 0) for n in namespaces)
    efficiency = round((total_daily - idle_cost) / max(total_daily, 0.01) * 100, 1)
    return {"namespaces": len(namespaces), "daily_cost": round(total_daily, 2),
            "idle_cost": round(idle_cost, 2), "efficiency_pct": efficiency}
