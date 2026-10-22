"""Webhook signature — HMAC signing and verification for webhook payloads."""

import hashlib
import hmac
import time


def sign_payload(*, payload: str, secret: str, timestamp: int | None = None) -> dict:
    ts = timestamp or int(time.time())
    message = f"{ts}.{payload}"
    signature = hmac.HMAC(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {"signature": f"v1={signature}", "timestamp": ts, "header": f"t={ts},v1={signature}"}


def verify_signature(*, payload: str, secret: str, header: str, tolerance_seconds: int = 300) -> dict:
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts = int(parts.get("t", "0"))
    sig = parts.get("v1", "")
    now = int(time.time())
    if abs(now - ts) > tolerance_seconds:
        return {"valid": False, "error": "Timestamp too old or too far in the future"}
    expected = hmac.HMAC(secret.encode(), f"{ts}.{payload}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {"valid": False, "error": "Signature mismatch"}
    return {"valid": True, "error": None}
