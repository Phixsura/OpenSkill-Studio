"""Fleet API Capacity Planning v9 — track API capacity and growth forecast."""
from __future__ import annotations
def fleet_api_capacity_planning_v9(apis: list[dict]) -> dict:
    growth_rate = sum(a.get("growth_pct_monthly", 0) for a in apis) / len(apis) if apis else 0
    current_capacity = sum(a.get("max_rps", 0) for a in apis)
    utilization = sum(a.get("utilization_pct", 0) for a in apis) / len(apis) if apis else 0
    return {"apis": len(apis), "growth_rate_pct": round(growth_rate, 1),
            "total_capacity_rps": current_capacity, "avg_utilization_pct": round(utilization, 1),
            "healthy": utilization < 80}
