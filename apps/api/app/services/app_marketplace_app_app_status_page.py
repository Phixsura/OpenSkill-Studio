"""Status page — system health status dashboard."""

import html
from datetime import datetime, timezone

STATUS_ICONS = {"operational": "🟢", "degraded": "🟡", "outage": "🔴", "maintenance": "🔵"}


def build_status_page(*, services: list[dict], incidents: list[dict] | None = None) -> dict:
    items = []
    overall = "operational"
    for svc in services:
        status = svc.get("status", "operational")
        if status == "outage":
            overall = "outage"
        elif status == "degraded" and overall != "outage":
            overall = "degraded"
        elif status == "maintenance" and overall == "operational":
            overall = "maintenance"
        items.append({
            "name": html.escape(svc.get("name", "")),
            "status": status,
            "icon": STATUS_ICONS.get(status, "⚪"),
            "uptime_pct": svc.get("uptime_pct", 100.0),
            "response_ms": svc.get("response_ms"),
        })
    inc = []
    for i in (incidents or []):
        inc.append({
            "title": html.escape(i.get("title", "")),
            "status": i.get("status", "investigating"),
            "timestamp": i.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    return {"services": items, "overall": overall, "overall_icon": STATUS_ICONS.get(overall, "⚪"),
            "incidents": inc, "updated_at": datetime.now(timezone.utc).isoformat()}
