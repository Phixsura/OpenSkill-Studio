"""App install guard — pre-flight checks before installation."""

def pre_install_check(
    *,
    app_status: str,
    org_app_count: int,
    max_apps_per_org: int = 50,
    blocked_categories: list[str] | None = None,
    app_category: str = "",
) -> dict:
    """Run pre-flight checks before installing an app."""
    errors = []
    warnings = []

    if app_status != "published":
        errors.append(f"App not published (status: {app_status})")
    if org_app_count >= max_apps_per_org:
        errors.append(f"Organization has reached app limit ({max_apps_per_org})")
    if blocked_categories and app_category in blocked_categories:
        errors.append(f"Category '{app_category}' is blocked for this organization")
    if org_app_count >= max_apps_per_org * 0.8:
        warnings.append(f"Organization is nearing app limit ({org_app_count}/{max_apps_per_org})")

    return {"allowed": len(errors) == 0, "errors": errors, "warnings": warnings}
