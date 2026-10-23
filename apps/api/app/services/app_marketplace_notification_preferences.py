"""Notification preferences — manage user notification settings."""


def get_notification_preferences(*, user_id: str) -> dict:
    channels = ["email", "push", "in_app", "slack"]
    categories = [
        {"key": "app_updates", "label": "App Updates", "description": "When apps you installed are updated"},
        {"key": "review_replies", "label": "Review Replies", "description": "Replies to your reviews"},
        {"key": "security_alerts", "label": "Security Alerts", "description": "Security-related notifications", "locked": True},
        {"key": "billing", "label": "Billing", "description": "Payment and subscription notifications"},
        {"key": "marketing", "label": "Marketing", "description": "Tips and feature announcements"},
    ]
    defaults = {}
    for cat in categories:
        defaults[cat["key"]] = {ch: True for ch in channels}
        if cat["key"] == "marketing":
            defaults[cat["key"]]["push"] = False
    return {
        "user_id": user_id,
        "channels": channels,
        "categories": categories,
        "preferences": defaults,
    }


def update_notification_preference(*, user_id: str, category: str,
                                     channel: str, enabled: bool) -> dict:
    locked = ["security_alerts"]
    if category in locked:
        return {"success": False, "error": "Security alerts cannot be disabled"}
    return {"success": True, "user_id": user_id, "category": category,
            "channel": channel, "enabled": enabled}
