"""Distributed lock manager — coordinate access to shared resources."""
from __future__ import annotations
import secrets
import time

_locks: dict[str, dict] = {}


def acquire_lock(resource: str, owner: str, ttl_sec: int = 30) -> dict:
    now = time.time()
    existing = _locks.get(resource)
    if existing and existing["expires_at"] > now:
        return {"acquired": False, "held_by": existing["owner"],
                "expires_in": round(existing["expires_at"] - now, 1)}
    token = secrets.token_urlsafe(16)
    _locks[resource] = {"resource": resource, "owner": owner, "token": token,
                         "acquired_at": now, "expires_at": now + ttl_sec}
    return {"acquired": True, "token": token, "resource": resource, "ttl_sec": ttl_sec}


def release_lock(resource: str, token: str) -> dict:
    lock = _locks.get(resource)
    if not lock:
        return {"released": False, "error": "not_found"}
    if lock["token"] != token:
        return {"released": False, "error": "token_mismatch"}
    del _locks[resource]
    return {"released": True, "resource": resource}


def extend_lock(resource: str, token: str, extra_sec: int = 30) -> dict:
    lock = _locks.get(resource)
    if not lock or lock["token"] != token:
        return {"extended": False, "error": "not_found_or_mismatch"}
    lock["expires_at"] += extra_sec
    return {"extended": True, "new_ttl": round(lock["expires_at"] - time.time(), 1)}


def list_locks() -> list[dict]:
    now = time.time()
    return [{"resource": l["resource"], "owner": l["owner"],
             "ttl_remaining": round(max(0, l["expires_at"] - now), 1)}
            for l in _locks.values() if l["expires_at"] > now]


def clear_locks() -> None:
    _locks.clear()
