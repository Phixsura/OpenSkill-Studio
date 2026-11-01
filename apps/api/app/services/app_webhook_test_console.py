"""Webhook test console — interactive webhook testing for developers."""

from datetime import UTC, datetime
from app.services.app_webhook_test_payload import generate_test_payload
from app.services.webhook_verify import sign_payload


def prepare_test_delivery(*, event_type: str, webhook_url: str, webhook_secret: str) -> dict:
    """Prepare a complete test delivery with signed payload."""
    import json
    payload_data = generate_test_payload(event_type)
    payload_bytes = json.dumps(payload_data).encode()
    signature = sign_payload(payload_bytes, webhook_secret)
    return {
        "url": webhook_url,
        "method": "POST",
        "headers": {
            "Content-Type": "application/json",
            "X-OpenSkill-Event": event_type,
            "X-OpenSkill-Signature": signature,
            "X-OpenSkill-Timestamp": datetime.now(UTC).isoformat(),
            "User-Agent": "OpenSkill-Webhooks/1.0 (test)",
        },
        "body": payload_data,
        "payload_size": len(payload_bytes),
    }
