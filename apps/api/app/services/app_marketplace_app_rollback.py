"""Rollback — revert installation to a previous version."""

from datetime import datetime, timezone


def can_rollback(*, installation: dict, available_versions: list[dict]) -> dict:
    current_version_id = installation.get("app_version_id")
    previous = [v for v in available_versions if v["id"] != current_version_id and v.get("review_status") == "approved"]
    if not previous:
        return {"can_rollback": False, "reason": "No previous approved version available"}
    latest_previous = max(previous, key=lambda v: v.get("released_at", ""))
    return {"can_rollback": True, "target_version": latest_previous, "reason": None}


def execute_rollback(*, installation_id: str, target_version_id: str, reason: str) -> dict:
    return {
        "installation_id": installation_id, "target_version_id": target_version_id,
        "reason": reason, "status": "rolled_back",
        "rolled_back_at": datetime.now(timezone.utc).isoformat(),
    }


def build_rollback_confirmation(*, app_name: str, from_version: str, to_version: str) -> dict:
    return {
        "message": f"Rolled back {app_name} from {from_version} to {to_version}",
        "warnings": ["Configuration may need manual adjustment", "Webhooks will be reconfigured"],
    }
