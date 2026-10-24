"""App API status — API health and performance monitoring."""

import html
from datetime import datetime, timezone


def build_api_status(*, services: list[dict]) -> dict:
    items = []
    total_latency = 0
    healthy = degraded = down = 0
    for s in services:
        status = s.get("status", "healthy")
        latency = s.get("avg_latency_ms", 0)
        total_latency += latency
        if status == "healthy": healthy += 1
        elif status == "degraded": degraded += 1
        else: down += 1
        items.append({
            "name": html.escape(s.get("name", "")),
            "status": status,
            "uptime_pct": s.get("uptime_pct", 100),
            "avg_latency_ms": latency,
            "error_rate_pct": s.get("error_rate_pct", 0),
            "icon": {"healthy": "🟢", "degraded": "🟡", "down": "🔴"}.get(status, "⚪"),
        })
    avg_latency = round(total_latency / max(len(items), 1))
    overall = "operational" if down == 0 and degraded == 0 else "degraded" if down == 0 else "outage"
    return {"services": items, "total": len(items),
            "healthy": healthy, "degraded": degraded, "down": down,
            "overall": overall, "avg_latency_ms": avg_latency,
            "checked_at": datetime.now(timezone.utc).isoformat()}
