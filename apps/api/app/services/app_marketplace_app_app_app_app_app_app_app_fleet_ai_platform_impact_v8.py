"""Fleet AI Impact v8 — track ultimate platform business impact."""
from __future__ import annotations
def fleet_ai_impact_v8(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    revenue = round(sum(t.get("revenue_usd", 0) for t in trackers), 2)
    savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    productivity = round(sum(t.get("prod_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    return {"trackers": len(trackers), "active": len(active), "revenue": revenue,
            "savings": savings, "productivity": productivity, "impactful": revenue > 0}
