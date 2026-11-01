"""Platform status page — public status page for all services."""

import html
from datetime import datetime, timezone

PLATFORM_SERVICES = [
    {"id": "api", "name": "API Gateway", "group": "Core"},
    {"id": "web", "name": "Web App", "group": "Core"},
    {"id": "auth", "name": "Authentication", "group": "Core"},
    {"id": "db", "name": "Database", "group": "Infrastructure"},
    {"id": "cache", "name": "Cache (Redis)", "group": "Infrastructure"},
    {"id": "storage", "name": "Object Storage", "group": "Infrastructure"},
    {"id": "webhooks", "name": "Webhook Delivery", "group": "Services"},
    {"id": "analytics", "name": "Analytics Engine", "group": "Services"},
    {"id": "search", "name": "Search Index", "group": "Services"},
    {"id": "cdn", "name": "CDN", "group": "Edge"},
]


def build_platform_status_page(*, statuses: dict[str, str],
                                   incidents: list[dict] | None = None) -> dict:
    groups: dict[str, list] = {}
    healthy = degraded = down = 0
    for svc in PLATFORM_SERVICES:
        status = statuses.get(svc["id"], "operational")
        icon = {"operational": "🟢", "degraded": "🟡", "outage": "🔴", "maintenance": "🔵"}.get(status, "⚪")
        if status == "operational": healthy += 1
        elif status == "degraded": degraded += 1
        elif status == "outage": down += 1
        groups.setdefault(svc["group"], []).append({
            "id": svc["id"], "name": svc["name"], "status": status, "icon": icon})
    overall = "operational" if down == 0 and degraded == 0 else "degraded" if down == 0 else "outage"
    inc = [{"title": html.escape(i.get("title", "")), "status": i.get("status", "investigating"),
            "updated": i.get("updated", "")} for i in (incidents or [])]
    return {"groups": groups, "overall": overall,
            "overall_label": {"operational": "All Systems Operational", "degraded": "Partial Degradation",
                               "outage": "Service Outage"}.get(overall, "Unknown"),
            "healthy": healthy, "degraded": degraded, "down": down,
            "incidents": inc, "updated_at": datetime.now(timezone.utc).isoformat()}
