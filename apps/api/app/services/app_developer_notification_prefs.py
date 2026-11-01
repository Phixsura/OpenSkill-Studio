"""Developer notification preferences — manage what notifications to receive."""

_prefs: dict[str, dict] = {}

DEFAULT_PREFS = {
    "app_installed": True,
    "app_uninstalled": True,
    "review_submitted": True,
    "review_decided": True,
    "app_revoked": True,
    "version_published": True,
    "health_alert": True,
    "weekly_summary": True,
    "email_enabled": True,
    "webhook_enabled": False,
}


def get_prefs(developer_id: str) -> dict:
    return {**DEFAULT_PREFS, **_prefs.get(developer_id, {})}


def update_prefs(developer_id: str, updates: dict) -> dict:
    if developer_id not in _prefs:
        _prefs[developer_id] = {}
    for k, v in updates.items():
        if k in DEFAULT_PREFS and isinstance(v, bool):
            _prefs[developer_id][k] = v
    return get_prefs(developer_id)


def should_notify(developer_id: str, event_type: str) -> bool:
    prefs = get_prefs(developer_id)
    return prefs.get(event_type, True) and prefs.get("email_enabled", True)
