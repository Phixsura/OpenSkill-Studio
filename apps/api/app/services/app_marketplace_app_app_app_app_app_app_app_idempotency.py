"""Idempotency key store — prevent duplicate API operations."""
from __future__ import annotations
import time

_keys: dict[str, dict] = {}


def check_or_store(key: str, ttl_sec: int = 86400) -> dict:
    now = time.time()
    existing = _keys.get(key)
    if existing:
        if now < existing["expires_at"]:
            return {"is_duplicate": True, "original_response": existing["response"],
                    "created_at": existing["created_at"]}
        del _keys[key]
    _keys[key] = {"key": key, "created_at": now, "expires_at": now + ttl_sec,
                   "response": None}
    return {"is_duplicate": False, "key": key}


def store_response(key: str, response: dict) -> dict:
    entry = _keys.get(key)
    if not entry:
        return {"stored": False, "error": "key_not_found"}
    entry["response"] = response
    return {"stored": True, "key": key}


def cleanup_expired() -> dict:
    now = time.time()
    expired = [k for k, v in _keys.items() if now >= v["expires_at"]]
    for k in expired:
        del _keys[k]
    return {"cleaned": len(expired), "remaining": len(_keys)}


def key_stats() -> dict:
    now = time.time()
    active = sum(1 for v in _keys.values() if now < v["expires_at"])
    with_response = sum(1 for v in _keys.values() if v["response"] is not None)
    return {"total": len(_keys), "active": active, "with_response": with_response}


def clear_keys() -> None:
    _keys.clear()
