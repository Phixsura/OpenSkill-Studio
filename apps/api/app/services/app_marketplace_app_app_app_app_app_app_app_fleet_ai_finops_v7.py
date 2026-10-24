"""Fleet AI FinOps v7 — track ultimate financial operations."""
from __future__ import annotations
def fleet_ai_finops_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    spend = round(sum(t.get("spend_usd", 0) for t in trackers), 2)
    savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    unit_economics = round(sum(t.get("cost_per_req", 0) for t in trackers) / max(len(trackers), 1), 6)
    roi = round(savings / max(spend, 1) * 100, 1)
    return {"trackers": len(trackers), "active": len(active), "spend": spend,
            "savings": savings, "cost_per_req": unit_economics, "roi": roi, "optimized": roi > 25}
