"""Fleet AI Platform Impact v7 — track AI platform business impact."""
from __future__ import annotations
def fleet_ai_platform_impact_v7(trackers: list[dict]) -> dict:
    active = [t for t in trackers if t.get("active", True)]
    revenue_impact = round(sum(t.get("revenue_usd", 0) for t in trackers), 2)
    cost_savings = round(sum(t.get("savings_usd", 0) for t in trackers), 2)
    productivity_gain = round(sum(t.get("prod_pct", 0) for t in trackers) / max(len(trackers), 1), 1)
    customer_impact = sum(t.get("customers_impacted", 0) for t in trackers)
    return {"trackers": len(trackers), "active": len(active), "revenue": revenue_impact,
            "savings": cost_savings, "productivity": productivity_gain, "customers": customer_impact, "impactful": revenue_impact > 0}
