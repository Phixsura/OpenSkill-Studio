"""Webhook debugger — interactive webhook testing and debugging tool."""

import secrets
import hashlib
import hmac
from datetime import datetime


def create_debug_endpoint(*, app_id: str) -> dict:
    endpoint_id = secrets.token_urlsafe(12)
    return {
        "endpoint_id": endpoint_id,
        "url": f"https://debug.openskill.dev/hooks/{endpoint_id}",
        "app_id": app_id,
        "created_at": datetime.utcnow().isoformat(),
        "expires_in_hours": 24,
        "received_count": 0,
    }


def inspect_delivery(*, payload: str, headers: dict, secret: str | None = None) -> dict:
    content_type = headers.get("content-type", headers.get("Content-Type", ""))
    sig_header = headers.get("x-signature", headers.get("X-Signature", ""))
    sig_valid = None
    if secret and sig_header:
        expected = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
        sig_valid = hmac.compare_digest(sig_header, expected)
    return {
        "payload_size": len(payload),
        "content_type": content_type,
        "has_signature": bool(sig_header),
        "signature_valid": sig_valid,
        "headers_count": len(headers),
        "timestamp": datetime.utcnow().isoformat(),
    }


def get_debug_stats(*, deliveries: list[dict]) -> dict:
    total = len(deliveries)
    valid_sigs = sum(1 for d in deliveries if d.get("signature_valid") is True)
    invalid_sigs = sum(1 for d in deliveries if d.get("signature_valid") is False)
    return {"total_deliveries": total, "valid_signatures": valid_sigs,
            "invalid_signatures": invalid_sigs,
            "avg_payload_size": round(sum(d.get("payload_size", 0) for d in deliveries) / max(total, 1))}
