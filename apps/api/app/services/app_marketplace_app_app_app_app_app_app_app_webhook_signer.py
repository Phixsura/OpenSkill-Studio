"""Webhook signature verifier — sign and verify webhook payloads with HMAC."""
from __future__ import annotations
import hashlib
import hmac
import json
import time
import secrets

_DEFAULT_KEY = secrets.token_bytes(32)


def sign_payload(payload: dict, *, secret: bytes = _DEFAULT_KEY,
                  timestamp: int | None = None) -> dict:
    ts = timestamp if timestamp is not None else int(time.time())
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    message = f"{ts}.{body}".encode()
    sig = hmac.new(secret, message, hashlib.sha256).hexdigest()
    return {"signature": f"v1={sig}", "timestamp": ts,
            "header": f"t={ts},v1={sig}"}


def verify_signature(payload: dict, *, header: str, secret: bytes = _DEFAULT_KEY,
                      tolerance: int = 300, now: int | None = None) -> dict:
    current = now if now is not None else int(time.time())
    parts = dict(p.split("=", 1) for p in header.split(",") if "=" in p)
    ts_str = parts.get("t", "0")
    sig = parts.get("v1", "")
    try:
        ts = int(ts_str)
    except ValueError:
        return {"valid": False, "reason": "invalid_timestamp"}
    if abs(current - ts) > tolerance:
        return {"valid": False, "reason": "timestamp_expired"}
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    expected = hmac.new(secret, f"{ts}.{body}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {"valid": False, "reason": "signature_mismatch"}
    return {"valid": True, "timestamp": ts}
