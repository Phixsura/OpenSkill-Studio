"""Webhook delivery headers — build standard webhook headers.

Follows industry conventions for webhook delivery headers:
- X-OpenSkill-Event: event type
- X-OpenSkill-Delivery: delivery ID
- X-OpenSkill-Signature: HMAC signature
- X-OpenSkill-Timestamp: delivery timestamp
"""

from datetime import UTC, datetime
from app.services.webhook_verify import sign_payload


def build_webhook_headers(
    *,
    event_type: str,
    delivery_id: str,
    payload: bytes,
    webhook_secret: str,
    timestamp: str | None = None,
) -> dict[str, str]:
    """Build standard webhook delivery headers."""
    ts = timestamp or datetime.now(UTC).isoformat()
    signature = sign_payload(payload, webhook_secret)

    return {
        "Content-Type": "application/json",
        "X-OpenSkill-Event": event_type,
        "X-OpenSkill-Delivery": delivery_id,
        "X-OpenSkill-Signature": signature,
        "X-OpenSkill-Timestamp": ts,
        "User-Agent": "OpenSkill-Webhooks/1.0",
    }


def extract_webhook_headers(headers: dict[str, str]) -> dict:
    """Extract OpenSkill webhook headers from a request."""
    return {
        "event_type": headers.get("X-OpenSkill-Event", ""),
        "delivery_id": headers.get("X-OpenSkill-Delivery", ""),
        "signature": headers.get("X-OpenSkill-Signature", "").removeprefix("sha256="),
        "timestamp": headers.get("X-OpenSkill-Timestamp", ""),
    }
