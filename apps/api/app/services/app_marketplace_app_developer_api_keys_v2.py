"""API keys v2 — enhanced key management with scopes, expiry, and usage tracking."""

import hashlib
import secrets
from datetime import datetime, timezone, timedelta


def create_api_key_v2(*, app_id: str, name: str, scopes: list[str],
                        expires_in_days: int | None = None) -> dict:
    raw = f"osk_{''.join(secrets.token_hex(24))}"
    prefix = raw[:12]
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    expires_at = None
    if expires_in_days:
        expires_at = (datetime.now(timezone.utc) + timedelta(days=expires_in_days)).isoformat()
    return {"app_id": app_id, "name": name, "prefix": prefix, "key_hash": key_hash,
            "scopes": scopes, "raw_key": raw, "expires_at": expires_at,
            "created_at": datetime.now(timezone.utc).isoformat(), "usage_count": 0}


def is_key_expired(*, key: dict) -> bool:
    expires = key.get("expires_at")
    if not expires:
        return False
    return datetime.now(timezone.utc).isoformat() > expires


def get_key_usage_summary(*, keys: list[dict]) -> dict:
    total_usage = sum(k.get("usage_count", 0) for k in keys)
    active = sum(1 for k in keys if not is_key_expired(key=k))
    expired = len(keys) - active
    return {"total_keys": len(keys), "active": active, "expired": expired, "total_usage": total_usage}
