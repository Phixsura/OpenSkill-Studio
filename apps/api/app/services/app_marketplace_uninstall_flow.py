"""Uninstall flow — revoke tokens, clean up secrets, deactivate installation."""

from datetime import datetime, timezone


def validate_uninstall(*, installation: dict, user: dict) -> dict:
    if installation.get("status") == "uninstalled":
        return {"valid": False, "error": "App is already uninstalled"}
    if installation.get("installed_by") != user.get("id") and not user.get("is_admin"):
        return {"valid": False, "error": "Only the installer or an admin can uninstall"}
    return {"valid": True, "error": None}


def build_cleanup_plan(*, installation: dict) -> list[dict]:
    steps = [
        {"action": "revoke_tokens", "description": "Revoke all API tokens issued to this app"},
        {"action": "delete_secrets", "description": "Remove stored secrets"},
        {"action": "disable_subscriptions", "description": "Disable all event subscriptions"},
        {"action": "deactivate", "description": "Mark installation as uninstalled"},
    ]
    if installation.get("has_webhooks"):
        steps.insert(2, {"action": "remove_webhooks", "description": "Remove webhook endpoints"})
    return steps


def execute_uninstall(*, installation: dict) -> dict:
    return {
        "installation_id": installation["id"],
        "status": "uninstalled",
        "uninstalled_at": datetime.now(timezone.utc).isoformat(),
        "cleanup_completed": True,
        "data_retained_until": None,
    }
