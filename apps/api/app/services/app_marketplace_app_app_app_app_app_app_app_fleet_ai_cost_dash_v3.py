"""Fleet AI Cost Dashboard v3 — track real-time AI infrastructure cost visualization."""
from __future__ import annotations
def fleet_ai_cost_dashboard_v3(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    total_cost = round(sum(d.get("total_usd", 0) for d in dashboards), 2)
    savings = round(sum(d.get("savings_usd", 0) for d in dashboards), 2)
    forecasts = sum(d.get("forecasts", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "total_usd": total_cost,
            "savings_usd": savings, "forecasts": forecasts, "optimizing": savings > 0}
