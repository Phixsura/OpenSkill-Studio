"""Fleet AI Model Analytics v2 — track deep model usage analytics."""
from __future__ import annotations
def fleet_ai_model_analytics_v2(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    models = sum(d.get("models", 0) for d in dashboards)
    dau = sum(d.get("dau", 0) for d in dashboards)
    requests_24h = sum(d.get("requests_24h", 0) for d in dashboards)
    revenue_24h = round(sum(d.get("revenue_usd", 0) for d in dashboards), 2)
    return {"dashboards": len(dashboards), "active": len(active), "models": models,
            "dau": dau, "requests_24h": requests_24h, "revenue_usd": revenue_24h, "growing": dau > 0}
