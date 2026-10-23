"""Multi-tenant config manager — per-org configuration with inheritance."""
from __future__ import annotations
import copy

DEFAULTS = {
    "theme": "light", "locale": "en", "timezone": "UTC",
    "features": {"analytics": True, "webhooks": True, "sandbox": False, "custom_domain": False},
    "limits": {"max_apps": 10, "max_users": 50, "max_storage_mb": 5000},
    "branding": {"logo_url": "", "accent_color": "#3B82F6", "app_name": "OpenSkill"},
}


def get_config(org_id: str, overrides: dict | None = None) -> dict:
    config = copy.deepcopy(DEFAULTS)
    if overrides:
        _deep_merge(config, overrides)
    return {"org_id": org_id, "config": config, "has_overrides": overrides is not None}


def update_config(current: dict, patch: dict) -> dict:
    updated = copy.deepcopy(current)
    _deep_merge(updated, patch)
    changed = [k for k in patch if k in current and current.get(k) != updated.get(k)]
    return {"config": updated, "changed_keys": changed}


def validate_config(config: dict) -> dict:
    errors = []
    limits = config.get("limits", {})
    if limits.get("max_apps", 0) < 1:
        errors.append("max_apps must be >= 1")
    if limits.get("max_users", 0) < 1:
        errors.append("max_users must be >= 1")
    theme = config.get("theme", "")
    if theme not in ("light", "dark", "system"):
        errors.append(f"Invalid theme: {theme}")
    return {"valid": len(errors) == 0, "errors": errors}


def _deep_merge(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _deep_merge(base[k], v)
        else:
            base[k] = v
