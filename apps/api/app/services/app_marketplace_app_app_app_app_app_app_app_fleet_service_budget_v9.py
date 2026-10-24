"""Fleet Service Budget v9 — track per-service cost budgets."""
from __future__ import annotations
def fleet_service_budget_v9(services: list[dict]) -> dict:
    over_budget = [s for s in services if s.get("spend", 0) > s.get("budget", float("inf"))]
    total_spend = sum(s.get("spend", 0) for s in services)
    total_budget = sum(s.get("budget", 0) for s in services)
    return {"services": len(services), "over_budget": len(over_budget), "total_spend": round(total_spend, 2),
            "total_budget": round(total_budget, 2), "healthy": len(over_budget) == 0}
