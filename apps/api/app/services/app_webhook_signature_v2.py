"""Webhook signature v2 — timestamp-based signature to prevent replay attacks."""

import hashlib
import hmac
import time


def sign_v2(*, payload: bytes, secret: str, timestamp: int | None = None) -> dict:
    """Sign payload with timestamp to prevent replay."""
    ts = timestamp or int(time.time())
    signed_payload = f"{ts}.".encode() + payload
    signature = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    return {"signature": f"v2={signature}", "timestamp": ts}


def verify_v2(*, payload: bytes, signature: str, timestamp: int, secret: str, max_age_seconds: int = 300) -> dict:
    """Verify v2 signature with replay protection."""
    now = int(time.time())
    if abs(now - timestamp) > max_age_seconds:
        return {"valid": False, "reason": "timestamp_expired"}
    
    signed_payload = f"{timestamp}.".encode() + payload
    expected = hmac.new(secret.encode(), signed_payload, hashlib.sha256).hexdigest()
    expected_sig = f"v2={expected}"
    
    if not hmac.compare_digest(signature, expected_sig):
        return {"valid": False, "reason": "signature_mismatch"}
    
    return {"valid": True}
