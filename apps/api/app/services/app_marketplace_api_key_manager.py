"""API Key Manager — issue, validate, rotate, and revoke developer API keys.

Provides secure API key lifecycle management for third-party developers
accessing the OpenSkill platform APIs.
"""
from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timezone


_keys: dict[str, dict] = {}  # key_hash -> key_record


def _hash_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()


def issue_key(
    developer_id: str,
    name: str,
    scopes: list[str],
    rate_limit: int = 1000,
) -> dict:
    """Issue a new API key for a developer."""
    raw_key = f"osk_{secrets.token_urlsafe(32)}"
    key_hash = _hash_key(raw_key)
    now = datetime.now(timezone.utc).isoformat()
    record = {
        "key_hash": key_hash,
        "key_prefix": raw_key[:8],
        "developer_id": developer_id,
        "name": name,
        "scopes": scopes,
        "rate_limit": rate_limit,
        "created_at": now,
        "last_used_at": None,
        "usage_count": 0,
        "active": True,
    }
    _keys[key_hash] = record
    return {"api_key": raw_key, **record}


def validate_key(api_key: str) -> dict | None:
    """Validate an API key and return its record if active."""
    key_hash = _hash_key(api_key)
    record = _keys.get(key_hash)
    if record and record["active"]:
        record["usage_count"] += 1
        record["last_used_at"] = datetime.now(timezone.utc).isoformat()
        return record
    return None


def revoke_key(api_key: str) -> bool:
    """Revoke an API key."""
    key_hash = _hash_key(api_key)
    record = _keys.get(key_hash)
    if record:
        record["active"] = False
        return True
    return False


def rotate_key(old_api_key: str) -> dict | None:
    """Rotate: revoke old key and issue a new one with same config."""
    key_hash = _hash_key(old_api_key)
    old_record = _keys.get(key_hash)
    if not old_record or not old_record["active"]:
        return None
    revoke_key(old_api_key)
    return issue_key(
        old_record["developer_id"], old_record["name"],
        old_record["scopes"], old_record["rate_limit"],
    )


def list_keys(developer_id: str, include_revoked: bool = False) -> list[dict]:
    """List API keys for a developer."""
    keys = [k for k in _keys.values() if k["developer_id"] == developer_id]
    if not include_revoked:
        keys = [k for k in keys if k["active"]]
    return keys


def check_scope(api_key: str, required_scope: str) -> bool:
    """Check if an API key has a specific scope."""
    record = validate_key(api_key)
    if not record:
        return False
    return required_scope in record["scopes"] or "*" in record["scopes"]
