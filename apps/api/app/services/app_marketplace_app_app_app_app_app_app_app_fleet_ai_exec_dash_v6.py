"""Fleet AI Executive Dashboard v6 — track C-suite platform overview."""
from __future__ import annotations
def fleet_ai_exec_dashboard_v6(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    revenue = round(sum(d.get("revenue_usd", 0) for d in dashboards), 2)
    cost = round(sum(d.get("cost_usd", 0) for d in dashboards), 2)
    margin = round((revenue - cost) / max(revenue, 1) * 100, 1)
    users = sum(d.get("users", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "revenue": revenue,
            "cost": cost, "margin": margin, "users": users, "profitable": margin > 50}
