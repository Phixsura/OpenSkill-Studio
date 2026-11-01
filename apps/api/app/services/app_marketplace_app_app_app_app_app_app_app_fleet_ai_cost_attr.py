"""Fleet AI Cost Attribution — track per-team AI spending."""
from __future__ import annotations
def fleet_ai_cost_attribution(teams: list[dict]) -> dict:
    total_cost = sum(t.get("monthly_cost", 0) for t in teams)
    top_spender = max(teams, key=lambda t: t.get("monthly_cost", 0)) if teams else None
    return {"teams": len(teams), "total_monthly": round(total_cost, 2),
            "top_spender": top_spender.get("name") if top_spender else None,
            "tracked": len(teams) > 0}
