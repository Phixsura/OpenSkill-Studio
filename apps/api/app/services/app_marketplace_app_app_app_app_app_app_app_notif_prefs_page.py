"""Notification preferences page — complete notification settings view."""
from __future__ import annotations

CATEGORIES = [
    {"id": "security", "label": "Security Alerts", "icon": "🔒", "default": True, "force": True},
    {"id": "deploys", "label": "Deployments", "icon": "🚀", "default": True, "force": False},
    {"id": "reviews", "label": "Reviews", "icon": "⭐", "default": True, "force": False},
    {"id": "billing", "label": "Billing", "icon": "💳", "default": True, "force": True},
    {"id": "marketing", "label": "Product Updates", "icon": "📢", "default": False, "force": False},
    {"id": "community", "label": "Community", "icon": "💬", "default": False, "force": False},
]
CHANNELS = ["email", "in_app", "slack", "push"]


def build_notification_prefs(overrides: dict[str, dict] | None = None) -> dict:
    prefs = []
    for cat in CATEGORIES:
        cat_prefs = (overrides or {}).get(cat["id"], {})
        channels = {ch: cat_prefs.get(ch, cat["default"]) if not cat["force"] else True
                     for ch in CHANNELS}
        prefs.append({**cat, "channels": channels, "editable": not cat["force"]})
    enabled = sum(1 for p in prefs for ch, v in p["channels"].items() if v)
    return {"categories": prefs, "channels": CHANNELS,
            "total_enabled": enabled, "total_possible": len(CATEGORIES) * len(CHANNELS)}
