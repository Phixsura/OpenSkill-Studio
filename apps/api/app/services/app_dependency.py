"""App dependency checker — detects and validates inter-app dependencies.

Checks if uninstalling/revoking an app would break other installed apps
that depend on its event subscriptions or API endpoints.
"""

import structlog

log = structlog.get_logger()


def check_uninstall_impact(
    *,
    app_id: str,
    app_event_types: list[str],
    all_subscriptions: list[dict],
) -> dict:
    """Check impact of uninstalling an app.
    
    Args:
        app_id: The app being uninstalled
        app_event_types: Events this app produces
        all_subscriptions: All active subscriptions [{app_id, event_type, installation_id}]
    
    Returns:
        {"safe": bool, "affected_apps": [...], "affected_subscriptions": [...]}
    """
    affected = []
    for sub in all_subscriptions:
        if sub.get("app_id") == app_id:
            continue  # Skip own subscriptions
        if sub.get("event_type") in app_event_types:
            affected.append(sub)

    affected_apps = list({s.get("app_id") for s in affected})
    return {
        "safe": len(affected) == 0,
        "affected_apps": affected_apps,
        "affected_subscriptions": affected,
        "total_impact": len(affected),
    }


def check_revoke_impact(
    *,
    app_id: str,
    active_installations: list[dict],
) -> dict:
    """Check impact of revoking an app (kill switch).
    
    Returns info about all active installations that would be affected.
    """
    affected = [i for i in active_installations if i.get("app_id") == app_id and i.get("status") == "active"]
    orgs = list({i.get("org_id") for i in affected})
    return {
        "safe": len(affected) == 0,
        "affected_installations": len(affected),
        "affected_orgs": orgs,
        "total_orgs": len(orgs),
    }


def validate_dependencies(
    *,
    required_permissions: list[str],
    granted_permissions: list[str],
) -> dict:
    """Validate an app has all required permissions.
    
    Returns {"satisfied": bool, "missing": [...]}
    """
    missing = [p for p in required_permissions if p not in granted_permissions]
    return {"satisfied": len(missing) == 0, "missing": missing}
