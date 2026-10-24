"""Webhook signature verifier — HMAC-based webhook signature with timestamp binding."""
from __future__ import annotations
import hashlib, hmac, time


def sign_payload(payload: str, secret: str, timestamp: int | None = None,
                 algorithm: str = "sha256") -> dict:
    ts = timestamp or int(time.time())
    signed_content = f"{ts}.{payload}"
    h = hmac.new(secret.encode(), signed_content.encode(), getattr(hashlib, algorithm))
    signature = h.hexdigest()
    return {"signature": signature, "timestamp": ts, "algorithm": algorithm,
            "header": f"t={ts},{algorithm}={signature}"}


def verify_signature(payload: str, secret: str, signature: str, timestamp: int,
                     algorithm: str = "sha256", tolerance_seconds: int = 300) -> dict:
    now = int(time.time())
    age = abs(now - timestamp)
    if age > tolerance_seconds:
        return {"valid": False, "reason": "timestamp_expired", "age_seconds": age}
    signed_content = f"{timestamp}.{payload}"
    expected = hmac.new(secret.encode(), signed_content.encode(),
                        getattr(hashlib, algorithm)).hexdigest()
    valid = hmac.compare_digest(expected, signature)
    return {"valid": valid, "algorithm": algorithm, "age_seconds": age,
            "reason": "ok" if valid else "signature_mismatch"}
