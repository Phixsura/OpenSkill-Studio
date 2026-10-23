"""App health monitor — continuous app health monitoring dashboard."""

import html
from datetime import datetime, timezone


def build_health_monitor(*, apps: list[dict]) -> dict:
    healthy = degraded = down = 0
    items = []
    for a in apps:
        status = a.get("status", "healthy")
        if status == "healthy": healthy += 1
        elif status == "degraded": degraded += 1
        else: down += 1
        items.append({
            "name": html.escape(a.get("name", "")), "icon": a.get("icon", "📦"),
            "status": status, "uptime_pct": a.get("uptime_pct", 100),
            "response_ms": a.get("response_ms", 0),
            "error_rate_pct": a.get("error_rate_pct", 0),
        })
    overall = "healthy" if down == 0 and degraded == 0 else "degraded" if down == 0 else "outage"
    return {"apps": items, "total": len(items), "healthy": healthy,
            "degraded": degraded, "down": down, "overall": overall,
            "checked_at": datetime.now(timezone.utc).isoformat()}
