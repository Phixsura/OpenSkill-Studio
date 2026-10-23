"""Notification preferences v2 — granular notification controls per event type and channel."""

EVENT_TYPES = {
    "app.installed": {"label": "New Installation", "default_channels": ["email", "in_app"]},
    "app.uninstalled": {"label": "App Uninstalled", "default_channels": ["in_app"]},
    "review.created": {"label": "New Review", "default_channels": ["email", "in_app"]},
    "version.approved": {"label": "Version Approved", "default_channels": ["email", "in_app", "slack"]},
    "error.spike": {"label": "Error Spike", "default_channels": ["email", "slack", "in_app"]},
    "quota.warning": {"label": "Quota Warning", "default_channels": ["email", "in_app"]},
    "security.alert": {"label": "Security Alert", "default_channels": ["email", "slack", "in_app"]},
}

CHANNELS = ["email", "slack", "in_app", "webhook"]


def get_default_preferences() -> dict:
    return {et: {"channels": list(cfg["default_channels"]), "enabled": True}
            for et, cfg in EVENT_TYPES.items()}


def update_preferences(*, current: dict, event_type: str, channels: list[str],
                          enabled: bool) -> dict:
    if event_type not in EVENT_TYPES:
        return {**current, "_error": f"Unknown event type: {event_type}"}
    invalid = set(channels) - set(CHANNELS)
    if invalid:
        return {**current, "_error": f"Invalid channels: {', '.join(invalid)}"}
    updated = dict(current)
    updated[event_type] = {"channels": channels, "enabled": enabled}
    return updated


def should_send(*, preferences: dict, event_type: str, channel: str) -> bool:
    pref = preferences.get(event_type, {})
    return pref.get("enabled", False) and channel in pref.get("channels", [])
