"""Fleet AI Platform Overview — track the complete AI platform at a glance."""
from __future__ import annotations
def fleet_ai_platform_overview(summaries: list[dict]) -> dict:
    services = sum(s.get("services", 0) for s in summaries)
    healthy = sum(s.get("healthy", 0) for s in summaries)
    models = sum(s.get("models", 0) for s in summaries)
    requests_24h = sum(s.get("requests_24h", 0) for s in summaries)
    uptime = round(sum(s.get("uptime_pct", 0) for s in summaries) / max(len(summaries), 1), 3)
    revenue = round(sum(s.get("revenue_usd", 0) for s in summaries), 2)
    return {"services": services, "healthy": healthy, "models": models,
            "requests_24h": requests_24h, "uptime": uptime, "revenue_usd": revenue,
            "status": "🟢 ALL OPERATIONAL" if healthy == services else "🟡 DEGRADED"}
