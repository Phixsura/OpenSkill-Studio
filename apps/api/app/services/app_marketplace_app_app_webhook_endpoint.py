"""Webhook endpoint — endpoint configuration and management."""

import html
import secrets
from urllib.parse import urlparse
from datetime import datetime, timezone


def create_webhook_endpoint(*, url: str, events: list[str],
                               description: str = "", active: bool = True) -> dict:
    parsed = urlparse(url)
    if parsed.scheme not in ("https",):
        return {"error": "Webhook URLs must use HTTPS"}
    endpoint_id = f"we_{secrets.token_hex(8)}"
    secret = f"whsec_{secrets.token_hex(24)}"
    return {
        "id": endpoint_id, "url": url, "events": events,
        "description": html.escape(description),
        "secret": secret, "secret_preview": secret[:12] + "••••••••",
        "active": active, "created_at": datetime.now(timezone.utc).isoformat(),
    }


def build_endpoint_list(*, endpoints: list[dict]) -> dict:
    active = sum(1 for e in endpoints if e.get("active"))
    total_events = sum(len(e.get("events", [])) for e in endpoints)
    return {"endpoints": endpoints, "total": len(endpoints),
            "active": active, "inactive": len(endpoints) - active,
            "total_event_subscriptions": total_events}
