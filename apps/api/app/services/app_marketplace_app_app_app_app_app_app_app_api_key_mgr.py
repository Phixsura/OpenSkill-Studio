"""API key manager — generate, validate, and rotate API keys."""
from __future__ import annotations
import secrets, hashlib, time


def generate_key(prefix: str = "osk") -> dict:
    raw = secrets.token_urlsafe(32)
    key = f"{prefix}_{raw}"
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    return {"key": key, "key_hash": key_hash, "prefix": prefix,
            "preview": f"{key[:8]}...{key[-4:]}",
            "created_at": time.time()}


def validate_key(key: str, stored_hash: str) -> dict:
    computed = hashlib.sha256(key.encode()).hexdigest()
    valid = secrets.compare_digest(computed, stored_hash)
    return {"valid": valid, "key_preview": f"{key[:8]}...{key[-4:]}" if len(key) > 12 else "***"}


def rotate_keys(keys: list[dict], max_age_days: int = 90) -> dict:
    now = time.time()
    to_rotate = []
    active = []
    for k in keys:
        age = (now - k["created_at"]) / 86400
        if age > max_age_days:
            to_rotate.append({**k, "age_days": round(age, 1)})
        else:
            active.append(k)
    return {"to_rotate": len(to_rotate), "active": len(active),
            "total": len(keys), "keys_needing_rotation": to_rotate}
