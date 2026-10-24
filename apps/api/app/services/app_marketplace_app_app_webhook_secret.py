"""Webhook secret — secure webhook secret management."""

import secrets
import hmac
import hashlib
from datetime import datetime, timezone


def generate_secret(*, prefix: str = "whsec") -> dict:
    raw = secrets.token_hex(32)
    return {"secret": f"{prefix}_{raw}", "prefix": prefix,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "preview": f"{prefix}_{raw[:8]}••••••••"}


def verify_payload(*, payload: str, secret: str, signature: str,
                     timestamp: int) -> dict:
    message = f"{timestamp}.{payload}"
    expected = "v1=" + hmac.new(secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    valid = hmac.compare_digest(expected, signature)
    now = int(datetime.now(timezone.utc).timestamp())
    age = now - timestamp
    too_old = age > 300
    return {"valid": valid and not too_old, "signature_valid": valid,
            "too_old": too_old, "age_seconds": age}
