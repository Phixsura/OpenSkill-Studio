"""Webhook signer — HMAC webhook payload signing and verification."""

import hmac
import hashlib
import secrets
import json
from datetime import datetime, timezone


def sign_webhook(*, payload: dict, secret: str, algorithm: str = "sha256") -> dict:
    body = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    timestamp = int(datetime.now(timezone.utc).timestamp())
    message = f"{timestamp}.{body}"
    if algorithm == "sha256":
        sig = hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    else:
        sig = hmac.new(secret.encode(), message.encode(), hashlib.sha512).hexdigest()
    return {"signature": f"v1={sig}", "timestamp": timestamp, "algorithm": algorithm,
            "headers": {"X-Webhook-Signature": f"v1={sig}", "X-Webhook-Timestamp": str(timestamp)}}


def verify_webhook(*, payload: str, signature: str, timestamp: int,
                    secret: str, max_age_s: int = 300) -> dict:
    message = f"{timestamp}.{payload}"
    expected = "v1=" + hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    valid_sig = hmac.compare_digest(expected, signature)
    now = int(datetime.now(timezone.utc).timestamp())
    too_old = (now - timestamp) > max_age_s
    return {"valid": valid_sig and not too_old, "signature_match": valid_sig,
            "age_s": now - timestamp, "too_old": too_old}


def generate_webhook_secret() -> dict:
    secret = f"whsec_{secrets.token_hex(24)}"
    return {"secret": secret, "length": len(secret)}
