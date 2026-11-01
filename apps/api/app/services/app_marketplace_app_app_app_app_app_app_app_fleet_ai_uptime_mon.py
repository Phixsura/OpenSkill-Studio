"""Fleet AI Uptime Monitor — track AI endpoint availability monitoring."""
from __future__ import annotations
def fleet_ai_uptime_monitor(monitors: list[dict]) -> dict:
    active = [m for m in monitors if m.get("active", True)]
    endpoints = sum(m.get("endpoints", 0) for m in monitors)
    uptime_pct = round(sum(m.get("uptime_pct", 0) for m in monitors) / max(len(monitors), 1), 3)
    checks_24h = sum(m.get("checks_24h", 0) for m in monitors)
    return {"monitors": len(monitors), "active": len(active), "endpoints": endpoints,
            "uptime_pct": uptime_pct, "checks_24h": checks_24h, "reliable": uptime_pct > 99.9}
