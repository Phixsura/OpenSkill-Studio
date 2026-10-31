"""API key rotation — automated key rotation with grace period."""

import secrets
import hmac
import hashlib
from datetime import datetime, timezone, timedelta

HMAC_KEY = secrets.token_bytes(32)


def rotate_key(*, current_prefix: str, grace_period_hours: int = 24) -> dict:
    new_key = f"osk_{secrets.token_hex(24)}"
    new_hash = hmac.new(HMAC_KEY, new_key.encode(), hashlib.sha256).hexdigest()[:16]
    now = datetime.now(timezone.utc)
    return {
        "new_key": new_key,
        "new_prefix": new_key[:8],
        "new_hash": new_hash,
        "old_prefix": current_prefix,
        "grace_until": (now + timedelta(hours=grace_period_hours)).isoformat(),
        "rotated_at": now.isoformat(),
        "old_key_valid_until": (now + timedelta(hours=grace_period_hours)).isoformat(),
    }


def check_rotation_status(*, rotated_at: str, grace_until: str) -> dict:
    now = datetime.now(timezone.utc)
    grace_dt = datetime.fromisoformat(grace_until.replace("Z", "+00:00"))
    if grace_dt.tzinfo is None:
        grace_dt = grace_dt.replace(tzinfo=timezone.utc)
    grace_expired = now > grace_dt
    return {"grace_expired": grace_expired, "old_key_active": not grace_expired,
            "status": "completed" if grace_expired else "in_grace_period"}
