"""Fleet AI Platform Summary v2 — track final comprehensive platform overview."""
from __future__ import annotations
def fleet_ai_platform_summary_v2(summaries: list[dict]) -> dict:
    services = sum(s.get("services", 0) for s in summaries)
    healthy = sum(s.get("healthy", 0) for s in summaries)
    requests_24h = sum(s.get("requests_24h", 0) for s in summaries)
    uptime = round(sum(s.get("uptime_pct", 0) for s in summaries) / max(len(summaries), 1), 3)
    cost_usd = round(sum(s.get("cost_usd", 0) for s in summaries), 2)
    return {"services": services, "healthy": healthy, "requests_24h": requests_24h,
            "uptime_pct": uptime, "cost_usd": cost_usd, "status": "🟢 ALL SYSTEMS OPERATIONAL" if healthy == services else "🟡 DEGRADED"}
