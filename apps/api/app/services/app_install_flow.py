"""Install flow — complete pre-install validation chain."""

from app.services.app_install_validator import validate_installation
from app.services.app_install_guard import pre_install_check


def validate_full_install_flow(*, app: dict, version: dict, org: dict, already_installed: bool) -> dict:
    """Run complete install validation."""
    errors = []
    warnings = []

    # Basic validation
    basic = validate_installation(
        app_status=app.get("status", ""),
        version_review_status=version.get("review_status", ""),
        already_installed=already_installed,
        required_permissions=app.get("manifest", {}).get("permissions", []),
    )
    errors.extend(basic.get("errors", []))
    warnings.extend(basic.get("warnings", []))

    # Org guard
    guard = pre_install_check(
        app_status=app.get("status", ""),
        org_app_count=org.get("app_count", 0),
        max_apps_per_org=org.get("max_apps", 50),
        app_category=app.get("category", ""),
    )
    errors.extend(guard.get("errors", []))
    warnings.extend(guard.get("warnings", []))

    return {"allowed": len(errors) == 0, "errors": errors, "warnings": warnings}
