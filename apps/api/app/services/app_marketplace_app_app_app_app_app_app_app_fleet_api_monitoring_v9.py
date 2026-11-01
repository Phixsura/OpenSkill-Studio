"""Fleet API Monitoring v9 — track comprehensive API monitoring dashboard."""
from __future__ import annotations
def fleet_api_monitoring_v9(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active")]
    alerts_firing = sum(m.get("alerts_firing", 0) for m in monitors)
    uptime = sum(m.get("uptime_pct", 0) for m in monitors) / len(monitors) if monitors else 0
    return {"monitors": len(monitors), "active": len(active), "alerts_firing": alerts_firing,
            "avg_uptime_pct": round(uptime, 2), "healthy": alerts_firing == 0}
