"""Fleet AI FinOps v8 — track ultimate AI financial operations."""
from __future__ import annotations
def fleet_ai_finops_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    spend = round(sum(t.get("spend_usd", 0) for t in trackers), 2)
    savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    unit_cost = round(sum(t.get("cost_per_req", 0) for t in trackers) / max(len(trackers), 1), 7)
    return {"trackers": len(trackers), "active": len(active), "spend": spend,
            "savings": savings, "unit_cost": unit_cost, "optimized": savings > spend * 0.25}
