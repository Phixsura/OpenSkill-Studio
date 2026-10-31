"""Uninstall summary — build data for uninstall confirmation dialog."""


def build_uninstall_summary(*, app_name: str, installation: dict, active_subscriptions: int,
                              active_automations: int, secrets_count: int) -> dict:
    warnings = []
    if active_subscriptions > 0:
        warnings.append(f"{active_subscriptions} event subscription(s) will stop")
    if active_automations > 0:
        warnings.append(f"{active_automations} automation rule(s) will be disabled")
    if secrets_count > 0:
        warnings.append(f"{secrets_count} secret(s) will be deleted")
    return {
        "app_name": app_name,
        "org_id": installation.get("org_id"),
        "warnings": warnings,
        "is_destructive": len(warnings) > 0,
        "data_will_be_deleted": ["event_subscriptions", "automation_rules", "secrets", "config"],
    }
