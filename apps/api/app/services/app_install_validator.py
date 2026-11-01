"""App installation validator — pre-install checks.

Validates that an app can be installed in an org:
- App status must be PUBLISHED
- Version must be APPROVED
- Org doesn't already have it installed
- Required permissions are acceptable
"""

import structlog

log = structlog.get_logger()


def validate_installation(
    *,
    app_status: str,
    version_review_status: str,
    already_installed: bool,
    required_permissions: list[str],
    org_allowed_permissions: list[str] | None = None,
) -> dict:
    """Pre-validate an app installation.
    
    Returns {"allowed": bool, "errors": [...], "warnings": [...]}
    """
    errors = []
    warnings = []

    if app_status != "published":
        errors.append(f"App is not published (status: {app_status})")

    if version_review_status != "approved":
        errors.append(f"Version not approved (review: {version_review_status})")

    if already_installed:
        errors.append("App is already installed in this organization")

    if org_allowed_permissions is not None:
        denied = [p for p in required_permissions if p not in org_allowed_permissions]
        if denied:
            errors.append(f"Organization does not allow permissions: {', '.join(denied)}")

    # Warnings for high-privilege permissions
    HIGH_PRIV = {"write:settings", "write:evaluations", "run:background_jobs"}
    high_privs = [p for p in required_permissions if p in HIGH_PRIV]
    if high_privs:
        warnings.append(f"App requests elevated permissions: {', '.join(high_privs)}")

    return {"allowed": len(errors) == 0, "errors": errors, "warnings": warnings}
