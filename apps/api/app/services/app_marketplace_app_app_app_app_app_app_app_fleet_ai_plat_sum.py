"""Fleet AI Platform Summary — track unified AI platform status overview."""
from __future__ import annotations
def fleet_ai_platform_summary(summaries: list[dict]) -> dict:
    total_services = sum(s.get("services", 0) for s in summaries)
    healthy = sum(s.get("healthy", 0) for s in summaries)
    total_requests = sum(s.get("requests_24h", 0) for s in summaries)
    uptime = round(sum(s.get("uptime_pct", 0) for s in summaries) / max(len(summaries), 1), 3)
    return {"services": total_services, "healthy": healthy, "requests_24h": total_requests,
            "uptime_pct": uptime, "status": "🟢 ALL SYSTEMS OPERATIONAL" if healthy == total_services else "🟡 DEGRADED"}
