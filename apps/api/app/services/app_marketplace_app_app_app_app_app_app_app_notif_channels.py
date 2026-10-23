"""Notification channel manager — configure delivery channels per user."""
from __future__ import annotations

CHANNELS = {
    "email": {"label": "Email", "icon": "📧", "supports": ["all"]},
    "slack": {"label": "Slack", "icon": "💬", "supports": ["alerts", "deploys", "mentions"]},
    "webhook": {"label": "Webhook", "icon": "🔗", "supports": ["all"]},
    "in_app": {"label": "In-App", "icon": "🔔", "supports": ["all"]},
    "sms": {"label": "SMS", "icon": "📱", "supports": ["critical"]},
}


def get_channels() -> list[dict]:
    return [{"id": k, **v} for k, v in CHANNELS.items()]


def build_channel_config(preferences: dict[str, bool]) -> dict:
    config = []
    for cid, info in CHANNELS.items():
        enabled = preferences.get(cid, cid in ("email", "in_app"))
        config.append({"id": cid, "label": info["label"], "icon": info["icon"],
                         "enabled": enabled, "supports": info["supports"]})
    enabled_count = sum(1 for c in config if c["enabled"])
    return {"channels": config, "enabled_count": enabled_count,
            "total": len(config)}
