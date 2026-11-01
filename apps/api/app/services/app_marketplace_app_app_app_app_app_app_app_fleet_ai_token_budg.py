"""Fleet AI Token Budget — track AI token usage and cost allocation."""
from __future__ import annotations
def fleet_ai_token_budget(budgets: list[dict]) -> dict:
    active = [b for b in budgets if b.get("active", True)]
    allocated = sum(b.get("allocated", 0) for b in budgets)
    used = sum(b.get("used", 0) for b in budgets)
    utilization = round(used / max(allocated, 1) * 100, 1)
    cost_usd = round(sum(b.get("cost_usd", 0) for b in budgets), 2)
    return {"budgets": len(budgets), "active": len(active), "allocated": allocated,
            "used": used, "utilization": utilization, "cost_usd": cost_usd, "within_budget": utilization < 90}
