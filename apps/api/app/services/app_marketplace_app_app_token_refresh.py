"""Token refresh — OAuth token rotation and refresh flow."""

import secrets
import hmac
import hashlib
from datetime import datetime, timezone, timedelta

HMAC_KEY = secrets.token_bytes(32)


def create_token_pair(*, user_id: str, access_ttl_min: int = 15,
                        refresh_ttl_days: int = 30) -> dict:
    access = secrets.token_urlsafe(32)
    refresh = secrets.token_urlsafe(48)
    now = datetime.now(timezone.utc)
    return {
        "access_token": access,
        "refresh_token": refresh,
        "access_expires_at": (now + timedelta(minutes=access_ttl_min)).isoformat(),
        "refresh_expires_at": (now + timedelta(days=refresh_ttl_days)).isoformat(),
        "token_type": "Bearer",
        "user_id": user_id,
    }


def rotate_refresh_token(*, old_refresh: str) -> dict:
    new_refresh = secrets.token_urlsafe(48)
    new_access = secrets.token_urlsafe(32)
    sig = hmac.new(HMAC_KEY, new_refresh.encode(), hashlib.sha256).hexdigest()[:16]
    return {"access_token": new_access, "refresh_token": new_refresh,
            "signature": sig, "rotated": True,
            "old_invalidated": True}


def is_token_expired(*, expires_at: str) -> bool:
    exp = datetime.fromisoformat(expires_at)
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    return datetime.now(timezone.utc) > exp
