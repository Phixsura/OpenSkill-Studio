"""Quick install — one-click install for apps with no required config."""


def can_quick_install(*, app: dict, has_config_schema: bool, new_permissions: list[str]) -> dict:
    """Check if an app can be installed with one click (no extra steps)."""
    return {
        "quick_install": not has_config_schema and len(new_permissions) == 0,
        "needs_config": has_config_schema,
        "needs_consent": len(new_permissions) > 0,
        "new_permissions": new_permissions,
        "steps_required": 1 + int(has_config_schema) + int(len(new_permissions) > 0),
    }
