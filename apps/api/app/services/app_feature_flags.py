"""App feature flags — enable/disable platform features per app/org.

Simple in-memory feature flag system for controlling
developer platform features during rollout.
"""

_flags: dict[str, dict] = {}

DEFAULT_FLAGS = {
    "sandbox_execution": True,
    "webhook_delivery": True,
    "ui_extensions": True,
    "event_subscriptions": True,
    "automation_rules": True,
    "marketplace_listing": True,
    "api_key_auth": True,
    "oauth_flow": True,
    "app_signing": False,  # Gradual rollout
    "event_replay": False,  # Beta feature
}


def get_flags(app_id: str) -> dict[str, bool]:
    """Get feature flags for an app (with defaults)."""
    overrides = _flags.get(app_id, {})
    return {**DEFAULT_FLAGS, **overrides}


def is_enabled(app_id: str, feature: str) -> bool:
    """Check if a feature is enabled for an app."""
    flags = get_flags(app_id)
    return flags.get(feature, False)


def set_flag(app_id: str, feature: str, enabled: bool) -> None:
    """Override a feature flag for an app."""
    if app_id not in _flags:
        _flags[app_id] = {}
    _flags[app_id][feature] = enabled


def reset_flags(app_id: str) -> None:
    """Reset all overrides for an app."""
    _flags.pop(app_id, None)


def list_features() -> list[str]:
    """List all available feature flags."""
    return sorted(DEFAULT_FLAGS.keys())
