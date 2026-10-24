"""Webhook signature verifier — HMAC-based webhook signature verification."""
from __future__ import annotations
import hashlib, hmac, time


def sign_payload(payload: str, secret: str, algorithm: str = "sha256") -> dict:
    h = hmac.new(secret.encode(), payload.encode(), getattr(hashlib, algorithm))
    signature = h.hexdigest()
    return {"signature": signature, "algorithm": algorithm,
            "header": f"{algorithm}={signature}"}


def verify_signature(payload: str, secret: str, signature: str,
                     algorithm: str = "sha256") -> dict:
    expected = hmac.new(secret.encode(), payload.encode(), getattr(hashlib, algorithm)).hexdigest()
    valid = hmac.compare_digest(expected, signature)
    return {"valid": valid, "algorithm": algorithm}


def verify_timestamp(timestamp: int, tolerance_seconds: int = 300) -> dict:
    now = int(time.time())
    age = abs(now - timestamp)
    valid = age <= tolerance_seconds
    return {"valid": valid, "age_seconds": age, "tolerance": tolerance_seconds}
