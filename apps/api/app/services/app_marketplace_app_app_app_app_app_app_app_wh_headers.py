"""Webhook header builder — construct standard webhook delivery headers."""
from __future__ import annotations
import hmac
import hashlib
import secrets
import time


def build_webhook_headers(*, payload: str, secret: str, event_type: str,
                            webhook_id: str = "") -> dict:
    timestamp = str(int(time.time()))
    msg = f"{timestamp}.{payload}"
    signature = hmac.new(secret.encode(), msg.encode(), hashlib.sha256).hexdigest()
    delivery_id = f"wh_{secrets.token_hex(8)}"
    return {
        "X-Webhook-Id": webhook_id or delivery_id,
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-Signature": f"v1={signature}",
        "X-Webhook-Event": event_type,
        "Content-Type": "application/json",
        "User-Agent": "OpenSkill-Webhooks/1.0",
    }


def verify_webhook_headers(*, headers: dict, payload: str, secret: str,
                              tolerance_sec: int = 300) -> dict:
    timestamp = headers.get("X-Webhook-Timestamp", "0")
    sig_header = headers.get("X-Webhook-Signature", "")
    if not sig_header.startswith("v1="):
        return {"valid": False, "reason": "invalid_signature_format"}
    sig = sig_header[3:]
    age = abs(int(time.time()) - int(timestamp))
    if age > tolerance_sec:
        return {"valid": False, "reason": "timestamp_expired", "age_sec": age}
    expected = hmac.new(secret.encode(), f"{timestamp}.{payload}".encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(sig, expected):
        return {"valid": False, "reason": "signature_mismatch"}
    return {"valid": True, "event": headers.get("X-Webhook-Event", "")}
