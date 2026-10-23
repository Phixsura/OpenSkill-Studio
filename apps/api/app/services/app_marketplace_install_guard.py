"""Install guard — pre-install checks to prevent conflicts and enforce requirements."""


def check_install_prerequisites(*, app: dict, org: dict, existing_installs: list[dict]) -> dict:
    blockers = []
    warnings = []
    # Check if already installed
    if any(i.get("app_id") == app.get("id") and i.get("status") == "active" for i in existing_installs):
        blockers.append({"type": "already_installed", "message": "This app is already installed"})
    # Check conflicts
    for conflict_id in app.get("conflicts_with", []):
        if any(i.get("app_id") == conflict_id and i.get("status") == "active" for i in existing_installs):
            blockers.append({"type": "conflict", "message": f"Conflicts with installed app {conflict_id}"})
    # Check dependencies
    for dep_id in app.get("depends_on", []):
        if not any(i.get("app_id") == dep_id and i.get("status") == "active" for i in existing_installs):
            blockers.append({"type": "missing_dependency", "message": f"Requires {dep_id} to be installed first"})
    # Check plan limits
    plan_limit = org.get("app_limit", 999)
    active_count = sum(1 for i in existing_installs if i.get("status") == "active")
    if active_count >= plan_limit:
        blockers.append({"type": "plan_limit", "message": f"App limit reached ({active_count}/{plan_limit})"})
    # Warnings
    if app.get("requires_admin"):
        warnings.append({"type": "admin_required", "message": "This app requires admin privileges"})
    return {"can_install": len(blockers) == 0, "blockers": blockers, "warnings": warnings}
