"""Webhook payload builder — construct delivery payloads with metadata."""

from datetime import UTC, datetime
import json


def build_delivery_payload(*, event_type: str, event_id: str, data: dict,
                           app_id: str, installation_id: str, org_id: str) -> bytes:
    """Build the full webhook delivery payload as bytes."""
    payload = {
        "event": event_type,
        "event_id": event_id,
        "data": data,
        "app_id": app_id,
        "installation_id": installation_id,
        "org_id": org_id,
        "delivered_at": datetime.now(UTC).isoformat(),
        "api_version": "2024-01-01",
    }
    return json.dumps(payload, separators=(",", ":"), default=str).encode()


def parse_delivery_payload(raw: bytes) -> dict | None:
    """Parse a webhook payload. Returns None on failure."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError):
        return None
