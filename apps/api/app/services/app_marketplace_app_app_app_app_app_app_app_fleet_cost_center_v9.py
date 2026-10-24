"""Fleet Cost Center v9 — track cost allocation by business unit."""
from __future__ import annotations
def fleet_cost_center_v9(centers: list[dict]) -> dict:
    total_spend = sum(c.get("monthly_spend", 0) for c in centers)
    over_budget = [c for c in centers if c.get("monthly_spend", 0) > c.get("budget", float("inf"))]
    teams = sum(c.get("teams", 0) for c in centers)
    return {"centers": len(centers), "total_spend": round(total_spend, 2), "over_budget": len(over_budget),
            "total_teams": teams, "healthy": len(over_budget) == 0}
