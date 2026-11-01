"""Fleet Capacity Planner v9 — forecast resource capacity needs."""
from __future__ import annotations
def fleet_capacity_planner_v9(resources: list[dict]) -> dict:
    used = sum(r.get("used", 0) for r in resources)
    total_cap = sum(r.get("capacity", 0) for r in resources)
    utilization = round(used / total_cap * 100, 1) if total_cap else 0
    return {"resources": len(resources), "used": used, "capacity": total_cap,
            "utilization_pct": utilization, "needs_scaling": utilization > 80,
            "healthy": utilization < 90}
