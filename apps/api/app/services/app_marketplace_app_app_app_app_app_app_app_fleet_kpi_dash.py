"""Fleet KPI dashboard — key platform indicators."""
from __future__ import annotations
def fleet_kpi_dashboard(kpis: dict) -> dict:
    uptime = kpis.get("uptime_pct", 99.9)
    user_growth = kpis.get("user_growth_pct", 0)
    revenue_growth = kpis.get("revenue_growth_pct", 0)
    healthy = uptime >= 99.9 and user_growth > 0
    return {"uptime_pct": uptime, "user_growth_pct": user_growth,
            "revenue_growth_pct": revenue_growth, "healthy": healthy}
