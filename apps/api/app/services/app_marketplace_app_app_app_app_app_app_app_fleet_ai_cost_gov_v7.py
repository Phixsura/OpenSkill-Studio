"""Fleet AI Cost Governance v7 — track ultimate cost governance."""
from __future__ import annotations
def fleet_ai_cost_governance_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    budgets = sum(s.get("budgets", 0) for s in systems)
    spend = round(sum(s.get("spend_usd", 0) for s in systems), 2)
    within_budget = all(s.get("within", True) for s in systems)
    return {"systems": len(systems), "active": len(active), "budgets": budgets,
            "spend": spend, "within_budget": within_budget, "governed": budgets > 0}
