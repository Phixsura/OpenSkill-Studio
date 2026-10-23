"""Changelog subscription — subscribe to app update notifications."""

import secrets
from datetime import datetime


def subscribe_to_changelog(*, user_id: str, app_id: str,
                             channels: list[str]) -> dict:
    valid_channels = {"email", "push", "slack", "webhook", "rss"}
    invalid = set(channels) - valid_channels
    if invalid:
        return {"error": f"Invalid channels: {', '.join(sorted(invalid))}"}
    if not channels:
        return {"error": "At least one channel required"}
    return {
        "subscription_id": f"clsub_{secrets.token_urlsafe(8)}",
        "user_id": user_id,
        "app_id": app_id,
        "channels": sorted(channels),
        "status": "active",
        "subscribed_at": datetime.utcnow().isoformat(),
    }


def get_subscriber_count(*, subscriptions: list[dict]) -> dict:
    by_channel: dict[str, int] = {}
    unique_users = set()
    for sub in subscriptions:
        unique_users.add(sub.get("user_id", ""))
        for ch in sub.get("channels", []):
            by_channel[ch] = by_channel.get(ch, 0) + 1
    return {
        "total_subscribers": len(unique_users),
        "by_channel": by_channel,
        "total_subscriptions": len(subscriptions),
    }
