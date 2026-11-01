"""App webhook config page — complete webhook configuration page."""

import html
import secrets
from urllib.parse import urlparse

EVENTS = {
    "App": ["app.installed", "app.uninstalled", "app.updated"],
    "Review": ["review.created", "review.updated"],
    "Deploy": ["deploy.started", "deploy.completed", "deploy.failed"],
    "System": ["webhook.test"],
}


def build_webhook_config_page(*, webhooks: list[dict]) -> dict:
    items = []
    for wh in webhooks:
        items.append({
            "id": wh.get("id", ""),
            "url": html.escape(wh.get("url", "")),
            "events": wh.get("events", []),
            "event_count": len(wh.get("events", [])),
            "active": wh.get("active", True),
            "success_rate": wh.get("success_rate", 100),
            "last_delivery": wh.get("last_delivery"),
        })
    active = sum(1 for i in items if i["active"])
    return {"webhooks": items, "total": len(items), "active": active,
            "available_events": EVENTS,
            "total_event_types": sum(len(v) for v in EVENTS.values()),
            "can_add": len(items) < 20}
