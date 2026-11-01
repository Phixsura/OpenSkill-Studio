"""Webhook setup wizard — guided webhook configuration."""

import html
import secrets
from urllib.parse import urlparse

EVENTS = ["app.installed", "app.updated", "app.deleted", "review.created",
          "deploy.completed", "deploy.failed", "webhook.test"]


def start_webhook_setup(*, url: str, events: list[str]) -> dict:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return {"error": "URL must use HTTPS"}
    invalid_events = [e for e in events if e not in EVENTS]
    if invalid_events:
        return {"error": f"Invalid events: {', '.join(invalid_events)}"}
    secret = f"whsec_{secrets.token_hex(24)}"
    return {
        "webhook_id": f"wh_{secrets.token_hex(8)}",
        "url": url, "events": events,
        "secret": secret,
        "secret_preview": secret[:12] + "••••••",
        "status": "active",
        "available_events": EVENTS,
        "setup_complete": True,
    }


def list_available_events() -> dict:
    categories: dict[str, list] = {}
    for e in EVENTS:
        cat = e.split(".")[0].title()
        categories.setdefault(cat, []).append(e)
    return {"events": EVENTS, "total": len(EVENTS),
            "categories": categories}
