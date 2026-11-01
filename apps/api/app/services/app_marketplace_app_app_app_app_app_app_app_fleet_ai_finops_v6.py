"""Fleet AI FinOps v6 — track AI financial operations at scale."""
from __future__ import annotations
def fleet_ai_finops_v6(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    monthly_spend = round(sum(t.get("spend_usd", 0) for t in trackers), 2)
    savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    unit_cost = round(sum(t.get("cost_per_req", 0) for t in trackers) / max(len(trackers), 1), 6)
    return {"trackers": len(trackers), "active": len(active), "spend": monthly_spend,
            "savings": savings, "cost_per_req": unit_cost, "optimized": savings > monthly_spend * 0.2}
