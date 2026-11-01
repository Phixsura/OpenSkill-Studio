"""Org settings for developer platform — per-org configuration."""

_settings: dict[str, dict] = {}

DEFAULTS = {
    "auto_upgrade_apps": True,
    "allow_third_party_apps": True,
    "max_apps_per_org": 50,
    "require_admin_approval": False,
    "blocked_categories": [],
    "allowed_permissions": None,  # None = allow all
}


def get_settings(org_id: str) -> dict:
    return {**DEFAULTS, **_settings.get(org_id, {})}


def update_settings(org_id: str, updates: dict) -> dict:
    if org_id not in _settings:
        _settings[org_id] = {}
    for k, v in updates.items():
        if k in DEFAULTS:
            _settings[org_id][k] = v
    return get_settings(org_id)
