"""API key manager — create, rotate, revoke keys with prefix visibility."""

import hashlib
import secrets
from datetime import datetime, timezone


def generate_api_key(*, app_id: str, name: str, scopes: list[str]) -> dict:
    raw_key = f"osk_{secrets.token_hex(24)}"
    prefix = raw_key[:8]
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    return {
        "app_id": app_id, "name": name, "prefix": prefix, "key_hash": key_hash,
        "scopes": scopes, "raw_key": raw_key, "status": "active",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "last_used_at": None,
    }


def rotate_key(*, old_key: dict) -> dict:
    new = generate_api_key(app_id=old_key["app_id"], name=old_key["name"], scopes=old_key["scopes"])
    return {"new_key": new, "old_key_status": "rotated", "grace_period_hours": 24}


def validate_key(*, raw_key: str, stored_hash: str) -> bool:
    return hashlib.sha256(raw_key.encode()).hexdigest() == stored_hash


def mask_key(*, prefix: str) -> str:
    return f"{prefix}{'•' * 40}"
