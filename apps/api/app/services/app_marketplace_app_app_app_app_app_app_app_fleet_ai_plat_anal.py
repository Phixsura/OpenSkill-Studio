"""Fleet AI Platform Analytics — track comprehensive platform usage insights."""
from __future__ import annotations
def fleet_ai_platform_analytics(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    dau = sum(d.get("dau", 0) for d in dashboards)
    mau = sum(d.get("mau", 0) for d in dashboards)
    api_calls_24h = sum(d.get("api_calls_24h", 0) for d in dashboards)
    revenue_24h = round(sum(d.get("revenue_usd", 0) for d in dashboards), 2)
    return {"dashboards": len(dashboards), "active": len(active), "dau": dau,
            "mau": mau, "api_calls_24h": api_calls_24h, "revenue_usd": revenue_24h, "growing": dau > 0}
