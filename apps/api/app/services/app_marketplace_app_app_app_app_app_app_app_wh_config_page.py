"""Webhook config page — build complete webhook management view."""
from __future__ import annotations
import html
from urllib.parse import urlparse


def build_webhook_config(webhooks: list[dict]) -> dict:
    items = []
    active = 0
    for wh in webhooks:
        url = wh.get("url", "")
        parsed = urlparse(url)
        secure = parsed.scheme == "https"
        items.append({
            "id": wh.get("id", ""), "url": url,
            "events": wh.get("events", []),
            "event_count": len(wh.get("events", [])),
            "active": wh.get("active", True),
            "secure": secure,
            "last_delivery": wh.get("last_delivery", "never"),
            "success_rate": wh.get("success_rate", 100),
        })
        if wh.get("active", True):
            active += 1
    return {"webhooks": items, "total": len(items), "active": active,
            "all_secure": all(i["secure"] for i in items) if items else True}
