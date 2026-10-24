"""Fleet Infra Cost v9 — track infrastructure cost allocation per team."""
from __future__ import annotations
def fleet_infra_cost_v9(teams: list[dict]) -> dict:
    total = sum(t.get("monthly_cost", 0) for t in teams)
    over_budget = [t for t in teams if t.get("monthly_cost", 0) > t.get("budget", float("inf"))]
    avg_cost = total / len(teams) if teams else 0
    return {"teams": len(teams), "total_monthly": round(total, 2), "over_budget": len(over_budget),
            "avg_per_team": round(avg_cost, 2), "healthy": len(over_budget) == 0}
