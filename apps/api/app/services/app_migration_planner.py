"""App version migration planner — plan and validate version migrations.

Generates migration plans for upgrading installations from one version to another,
including permission diffs, config changes, and rollback steps.
"""

from app.services.app_version_diff import diff_manifests


def create_migration_plan(
    *,
    from_version: str,
    to_version: str,
    old_manifest: dict,
    new_manifest: dict,
    installation_count: int = 0,
) -> dict:
    """Create a migration plan for upgrading between versions."""
    diff = diff_manifests(old_manifest, new_manifest)

    steps = []

    # Permission changes require consent
    if diff["permissions"]["added"]:
        steps.append({"action": "request_consent", "reason": f"New permissions: {', '.join(diff['permissions']['added'])}"})

    if diff["permissions"]["removed"]:
        steps.append({"action": "warn_removal", "reason": f"Removed permissions: {', '.join(diff['permissions']['removed'])}", "breaking": True})

    # Config schema changes need validation
    if diff["config_schema_changed"]:
        steps.append({"action": "validate_configs", "reason": "Config schema changed — existing configs need validation"})

    # Sandbox changes
    if diff["sandbox"]["changed"]:
        steps.append({"action": "update_sandbox", "reason": "Sandbox configuration changed"})

    # Final step
    steps.append({"action": "upgrade_installations", "count": installation_count})

    return {
        "from_version": from_version,
        "to_version": to_version,
        "breaking": diff["breaking"],
        "steps": steps,
        "total_steps": len(steps),
        "affected_installations": installation_count,
        "requires_consent": bool(diff["permissions"]["added"]),
        "diff_summary": diff["summary"],
    }


def validate_migration(plan: dict) -> dict:
    """Validate a migration plan is safe to execute."""
    errors = []
    warnings = []

    if plan["breaking"]:
        warnings.append("This is a breaking change — removed permissions may affect existing integrations")

    if plan["requires_consent"]:
        warnings.append("New permissions require user consent before migration")

    if plan["affected_installations"] > 100:
        warnings.append(f"Large migration: {plan['affected_installations']} installations affected")

    return {"safe": len(errors) == 0, "errors": errors, "warnings": warnings}
