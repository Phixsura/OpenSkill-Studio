"""Credential vault — encrypted credential storage and rotation."""

import secrets
import hashlib
import hmac
import html
from datetime import datetime, timezone, timedelta

HMAC_KEY = secrets.token_bytes(32)


def store_credential(*, name: str, value: str, rotation_days: int = 90) -> dict:
    cred_id = f"cred_{secrets.token_hex(8)}"
    value_hash = hmac.new(HMAC_KEY, value.encode(), hashlib.sha256).hexdigest()[:16]
    now = datetime.now(timezone.utc)
    return {"id": cred_id, "name": html.escape(name),
            "value_hash": value_hash, "preview": "•" * 16,
            "rotation_days": rotation_days,
            "created_at": now.isoformat(),
            "expires_at": (now + timedelta(days=rotation_days)).isoformat(),
            "status": "active"}


def check_rotation(*, credentials: list[dict]) -> dict:
    now = datetime.now(timezone.utc)
    expiring_soon = []
    expired = []
    for c in credentials:
        exp = c.get("expires_at", "")
        if exp:
            exp_dt = datetime.fromisoformat(exp.replace("Z", "+00:00")) if "Z" in exp else datetime.fromisoformat(exp)
            if exp_dt.tzinfo is None:
                exp_dt = exp_dt.replace(tzinfo=timezone.utc)
            if exp_dt < now:
                expired.append(c.get("name", ""))
            elif (exp_dt - now).days < 14:
                expiring_soon.append(c.get("name", ""))
    return {"total": len(credentials), "expired": expired, "expiring_soon": expiring_soon,
            "needs_attention": len(expired) + len(expiring_soon) > 0}
