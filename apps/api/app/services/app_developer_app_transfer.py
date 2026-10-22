"""App transfer — transfer app ownership between developers."""

from datetime import UTC, datetime

def create_transfer_request(*, app_id: str, from_developer: str, to_developer: str, reason: str = "") -> dict:
    return {"app_id": app_id, "from": from_developer, "to": to_developer, "reason": reason,
            "status": "pending", "created_at": datetime.now(UTC).isoformat()}

def validate_transfer(request: dict) -> list[str]:
    errors = []
    if request["from"] == request["to"]:
        errors.append("Cannot transfer to yourself")
    if not request.get("app_id"):
        errors.append("App ID required")
    return errors
