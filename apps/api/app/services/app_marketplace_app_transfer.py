"""App transfer — transfer ownership between developer accounts."""

from datetime import datetime, timezone


def initiate_transfer(*, app: dict, from_dev_id: str, to_dev_id: str, reason: str) -> dict:
    if from_dev_id == to_dev_id:
        return {"error": "Cannot transfer to yourself"}
    if app.get("status") == "suspended":
        return {"error": "Cannot transfer a suspended app"}
    return {
        "app_id": app["id"], "from_developer_id": from_dev_id, "to_developer_id": to_dev_id,
        "reason": reason, "status": "pending", "error": None,
        "initiated_at": datetime.now(timezone.utc).isoformat(),
        "expires_at": None,
    }


def accept_transfer(*, transfer: dict, accepting_dev_id: str) -> dict:
    if transfer["to_developer_id"] != accepting_dev_id:
        return {"error": "Only the target developer can accept"}
    if transfer["status"] != "pending":
        return {"error": f"Transfer is {transfer['status']}, not pending"}
    return {**transfer, "status": "completed", "completed_at": datetime.now(timezone.utc).isoformat(), "error": None}


def reject_transfer(*, transfer: dict, rejecting_dev_id: str) -> dict:
    if transfer["to_developer_id"] != rejecting_dev_id:
        return {"error": "Only the target developer can reject"}
    return {**transfer, "status": "rejected", "error": None}
