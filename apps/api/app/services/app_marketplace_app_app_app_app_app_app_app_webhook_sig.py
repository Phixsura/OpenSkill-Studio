"""Webhook signature verifier — sign and verify webhook payloads."""
from __future__ import annotations
import hashlib
import hmac
import time


def sign_payload(payload: str, secret: str, timestamp: int | None = None) -> dict:
    ts = timestamp or int(time.time())
    message = f"{ts}.{payload}"
    sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return {"signature": f"v1={sig}", "timestamp": ts,
            "header": f"t={ts},v1={sig}"}


def verify_signature(payload: str, header: str, secret: str, tolerance_sec: int = 300) -> dict:
    parts = {}
    for part in header.split(","):
        k, _, v = part.partition("=")
        parts[k] = v
    ts_str = parts.get("t", "")
    sig = parts.get("v1", "")
    if not ts_str or not sig:
        return {"valid": False, "error": "malformed_header"}
    try:
        ts = int(ts_str)
    except ValueError:
        return {"valid": False, "error": "invalid_timestamp"}
    now = int(time.time())
    if abs(now - ts) > tolerance_sec:
        return {"valid": False, "error": "timestamp_expired"}
    expected = hmac.new(secret.encode(), f"{ts}.{payload}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {"valid": False, "error": "signature_mismatch"}
    return {"valid": True, "timestamp": ts}
