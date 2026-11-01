"""Executive summary — one-page platform executive report."""
from __future__ import annotations


def generate_executive_summary(data: dict) -> dict:
    revenue = data.get("revenue", 0)
    apps = data.get("total_apps", 0)
    users = data.get("total_users", 0)
    uptime = data.get("uptime_pct", 99.9)
    nps = data.get("nps", 0)
    incidents = data.get("incidents_month", 0)
    
    health = "strong" if uptime >= 99.9 and nps >= 40 else "good" if uptime >= 99.5 else "at_risk"
    kpis = [
        {"name": "Revenue", "value": f"${revenue:,.0f}", "trend": data.get("revenue_trend", "flat")},
        {"name": "Apps", "value": f"{apps:,}", "trend": data.get("apps_trend", "flat")},
        {"name": "Users", "value": f"{users:,}", "trend": data.get("users_trend", "flat")},
        {"name": "Uptime", "value": f"{uptime}%", "trend": "stable"},
        {"name": "NPS", "value": str(nps), "trend": "up" if nps > 30 else "flat"},
        {"name": "Incidents", "value": str(incidents), "trend": "down" if incidents < 5 else "flat"},
    ]
    return {"health": health, "kpis": kpis, "summary": f"Platform {health} with {apps} apps serving {users:,} users at {uptime}% uptime"}
