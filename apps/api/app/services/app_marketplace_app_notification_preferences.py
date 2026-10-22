"""Notification preferences — per-user notification settings for app events."""

CHANNELS = {"email", "slack", "webhook", "in_app"}
EVENT_CATEGORIES = {"installs", "reviews", "errors", "updates", "security", "billing"}


def get_default_preferences() -> dict:
    return {cat: {"channels": ["in_app", "email"], "enabled": True} for cat in EVENT_CATEGORIES}


def update_preference(*, preferences: dict, category: str, channels: list[str],
                        enabled: bool) -> dict:
    if category not in EVENT_CATEGORIES:
        return {"error": f"Invalid category: {category}"}
    invalid = set(channels) - CHANNELS
    if invalid:
        return {"error": f"Invalid channels: {', '.join(invalid)}"}
    prefs = dict(preferences)
    prefs[category] = {"channels": channels, "enabled": enabled}
    return {"preferences": prefs, "error": None}


def should_notify(*, preferences: dict, category: str, channel: str) -> bool:
    pref = preferences.get(category, {})
    return pref.get("enabled", False) and channel in pref.get("channels", [])
