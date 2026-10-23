"""Access token — short-lived token generation with scopes."""

import secrets
import hashlib
import hmac
import html
from datetime import datetime, timezone, timedelta

HMAC_KEY = secrets.token_bytes(32)


def generate_access_token(*, user_id: str, scopes: list[str],
                            ttl_minutes: int = 60) -> dict:
    raw = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    sig = hmac.new(HMAC_KEY, raw.encode(), hashlib.sha256).hexdigest()[:16]
    now = datetime.now(timezone.utc)
    return {"token": raw, "token_hash": token_hash, "signature": sig,
            "user_id": user_id, "scopes": scopes,
            "issued_at": now.isoformat(),
            "expires_at": (now + timedelta(minutes=ttl_minutes)).isoformat(),
            "ttl_minutes": ttl_minutes}


def verify_token_signature(*, token: str, signature: str) -> bool:
    expected = hmac.new(HMAC_KEY, token.encode(), hashlib.sha256).hexdigest()[:16]
    return hmac.compare_digest(expected, signature)


def check_scope(*, required: str, granted: list[str]) -> dict:
    allowed = required in granted or "admin" in granted or "*" in granted
    return {"required": required, "granted": granted, "allowed": allowed}
