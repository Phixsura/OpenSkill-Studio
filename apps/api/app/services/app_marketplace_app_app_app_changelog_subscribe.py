"""App changelog subscribe — subscribe to app update notifications."""

import html
import re
import secrets
from datetime import datetime, timezone

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")


def subscribe_to_changelog(*, app_id: str, email: str, channels: list[str] | None = None) -> dict:
    if not EMAIL_RE.match(email):
        return {"error": "Invalid email address"}
    valid_channels = {"email", "rss", "slack", "webhook"}
    chans = [c for c in (channels or ["email"]) if c in valid_channels]
    return {
        "subscription_id": f"csub_{secrets.token_hex(6)}",
        "app_id": app_id, "email": email,
        "channels": chans, "status": "active",
        "subscribed_at": datetime.now(timezone.utc).isoformat(),
    }


def build_subscriber_stats(*, subscriptions: list[dict]) -> dict:
    active = sum(1 for s in subscriptions if s.get("status") == "active")
    by_channel: dict[str, int] = {}
    for s in subscriptions:
        for c in s.get("channels", []):
            by_channel[c] = by_channel.get(c, 0) + 1
    return {"total": len(subscriptions), "active": active,
            "by_channel": by_channel}
