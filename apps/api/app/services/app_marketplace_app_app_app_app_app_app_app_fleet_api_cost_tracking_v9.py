"""Fleet API Cost Tracking v9 — track per-API call cost allocation."""
from __future__ import annotations
def fleet_api_cost_tracking_v9(apis: list[dict]) -> dict:
    total_cost = sum(a.get("monthly_cost", 0) for a in apis)
    cost_per_call = total_cost / sum(a.get("calls_monthly", 1) for a in apis) if apis else 0
    over_budget = [a for a in apis if a.get("monthly_cost", 0) > a.get("budget", float("inf"))]
    return {"apis": len(apis), "total_monthly": round(total_cost, 2),
            "avg_cost_per_call": round(cost_per_call, 6), "over_budget": len(over_budget), "healthy": len(over_budget) == 0}
