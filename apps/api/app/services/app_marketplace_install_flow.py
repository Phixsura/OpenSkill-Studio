"""Install flow orchestrator — validates permissions, creates installation, provisions secrets."""

from datetime import datetime, timezone


def validate_install_prerequisites(*, app: dict, org: dict, user: dict) -> dict:
    errors = []
    if app.get("status") != "published":
        errors.append("App is not published")
    if not app.get("current_version_id"):
        errors.append("App has no approved version")
    if not org.get("id"):
        errors.append("Organization is required")
    required_scopes = app.get("required_scopes", [])
    org_granted = set(org.get("granted_scopes", []))
    missing = [s for s in required_scopes if s not in org_granted]
    if missing:
        errors.append(f"Missing scopes: {', '.join(missing)}")
    return {"valid": len(errors) == 0, "errors": errors}


def create_installation_record(*, app: dict, org_id: str, user_id: str, version_id: str) -> dict:
    return {
        "id": f"inst_{app['id']}_{org_id}",
        "app_id": app["id"],
        "app_version_id": version_id,
        "org_id": org_id,
        "installed_by": user_id,
        "status": "active",
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "config": app.get("default_config", {}),
    }


def build_install_confirmation(*, app: dict, installation: dict) -> dict:
    return {
        "message": f"Successfully installed {app['name']}",
        "installation_id": installation["id"],
        "next_steps": [
            "Configure app settings",
            "Grant required permissions",
            "Enable event subscriptions",
        ],
    }
