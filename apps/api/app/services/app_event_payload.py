"""Event payload builder — construct standardized event payloads."""

from datetime import UTC, datetime
import secrets


def build_event_payload(*, event_type: str, data: dict, org_id: str, source: str | None = None) -> dict:
    return {
        "event_id": f"evt_{secrets.token_urlsafe(16)}",
        "event_type": event_type,
        "data": data,
        "org_id": org_id,
        "source": source,
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
    }


def validate_event_payload(payload: dict) -> list[str]:
    errors = []
    for field in ["event_id", "event_type", "data", "timestamp"]:
        if field not in payload:
            errors.append(f"Missing field: {field}")
    if "event_type" in payload and "." not in payload["event_type"]:
        errors.append("Event type must be category.action format")
    return errors
