"""Fleet Chronosphere — track cloud-native observability."""
from __future__ import annotations
def fleet_chronosphere_status(tenants: list[dict]) -> dict:
    active_series = sum(t.get("active_series", 0) for t in tenants)
    cost_savings = sum(t.get("savings_pct", 0) for t in tenants) / max(len(tenants), 1)
    return {"tenants": len(tenants), "active_series": active_series,
            "avg_savings_pct": round(cost_savings, 1), "cost_efficient": cost_savings > 30}
