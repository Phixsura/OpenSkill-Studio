"""Fleet AI Global Status v7 — track worldwide platform operational status."""
from __future__ import annotations
def fleet_ai_global_status_v7(regions: list[dict]) -> dict:
    active = [r for r in regions if r.get("active", True)]
    total_services = sum(r.get("services", 0) for r in regions)
    healthy = sum(r.get("healthy", 0) for r in regions)
    requests_24h = sum(r.get("requests_24h", 0) for r in regions)
    uptime = round(sum(r.get("uptime_pct", 0) for r in regions) / max(len(regions), 1), 4)
    return {"regions": len(regions), "active": len(active), "services": total_services,
            "healthy": healthy, "requests_24h": requests_24h, "uptime": uptime,
            "global_status": "🟢 ALL REGIONS OPERATIONAL" if healthy == total_services else "🟡 DEGRADED"}
