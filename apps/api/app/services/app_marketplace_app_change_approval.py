"""Change approval — multi-stage approval workflow for app changes."""

from datetime import datetime, timezone

APPROVAL_TYPES = {"publish", "config_change", "permission_upgrade", "transfer", "delete"}


def create_approval_request(*, app_id: str, type: str, requester_id: str,
                               description: str, changes: dict) -> dict:
    if type not in APPROVAL_TYPES:
        return {"error": f"Invalid type. Use: {', '.join(sorted(APPROVAL_TYPES))}"}
    return {"app_id": app_id, "type": type, "requester_id": requester_id,
            "description": description, "changes": changes,
            "status": "pending", "approvers": [], "error": None,
            "created_at": datetime.now(timezone.utc).isoformat()}


def approve(*, request: dict, approver_id: str) -> dict:
    if approver_id == request.get("requester_id"):
        return {**request, "error": "Cannot approve your own request"}
    approvers = list(request.get("approvers", []))
    approvers.append({"user_id": approver_id, "action": "approved", "at": datetime.now(timezone.utc).isoformat()})
    return {**request, "approvers": approvers, "status": "approved", "error": None}


def reject(*, request: dict, rejector_id: str, reason: str) -> dict:
    return {**request, "status": "rejected", "rejection_reason": reason,
            "rejected_by": rejector_id, "error": None}
