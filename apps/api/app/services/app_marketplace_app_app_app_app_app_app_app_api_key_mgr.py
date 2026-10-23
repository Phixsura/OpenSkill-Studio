"""API key manager — create, revoke, and validate API keys."""
from __future__ import annotations
import secrets
import hashlib
import time

_keys: dict[str, dict] = {}


def create_key(name: str, scopes: list[str], expires_days: int = 365) -> dict:
    raw = f"osk_{secrets.token_urlsafe(32)}"
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    _keys[hashed] = {
        "name": name, "scopes": scopes, "hashed": hashed,
        "created_at": time.time(),
        "expires_at": time.time() + expires_days * 86400,
        "revoked": False, "last_used": None,
    }
    prefix = raw[:8]
    return {"key": raw, "prefix": prefix, "name": name, "scopes": scopes}


def validate_key(raw: str) -> dict:
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    entry = _keys.get(hashed)
    if not entry:
        return {"valid": False, "reason": "not_found"}
    if entry["revoked"]:
        return {"valid": False, "reason": "revoked"}
    if time.time() > entry["expires_at"]:
        return {"valid": False, "reason": "expired"}
    entry["last_used"] = time.time()
    return {"valid": True, "name": entry["name"], "scopes": entry["scopes"]}


def revoke_key(raw: str) -> dict:
    hashed = hashlib.sha256(raw.encode()).hexdigest()
    if hashed not in _keys:
        return {"revoked": False, "reason": "not_found"}
    _keys[hashed]["revoked"] = True
    return {"revoked": True, "name": _keys[hashed]["name"]}


def list_keys() -> list[dict]:
    return [{"name": v["name"], "prefix": v["hashed"][:8], "scopes": v["scopes"],
             "revoked": v["revoked"]} for v in _keys.values()]


def clear_keys() -> None:
    _keys.clear()
