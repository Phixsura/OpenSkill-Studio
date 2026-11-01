"""Webhook signature — sign and verify webhook payloads with HMAC."""

import hmac
import hashlib
import time
import secrets


def sign_payload(*, payload: str, secret: str, timestamp: int | None = None) -> dict:
    ts = timestamp or int(time.time())
    message = f"{ts}.{payload}"
    signature = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {
        "signature": f"v1={signature}",
        "timestamp": ts,
        "header": f"t={ts},v1={signature}",
    }


def verify_signature(*, payload: str, header: str, secret: str,
                       tolerance_sec: int = 300) -> dict:
    try:
        parts = dict(p.split("=", 1) for p in header.split(","))
    except ValueError:
        return {"valid": False, "error": "Malformed signature header"}
    ts_str = parts.get("t")
    sig = parts.get("v1")
    if not ts_str or not sig:
        return {"valid": False, "error": "Missing timestamp or signature"}
    try:
        ts = int(ts_str)
    except ValueError:
        return {"valid": False, "error": "Invalid timestamp"}
    now = int(time.time())
    if abs(now - ts) > tolerance_sec:
        return {"valid": False, "error": "Timestamp outside tolerance window"}
    message = f"{ts}.{payload}"
    expected = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {"valid": False, "error": "Signature mismatch"}
    return {"valid": True, "timestamp": ts}


def generate_webhook_secret() -> dict:
    secret = f"whsec_{secrets.token_urlsafe(24)}"
    return {"secret": secret, "warning": "Store this secret securely."}
