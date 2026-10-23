"""Distributed lock manager — acquire, release, and monitor distributed locks."""
from __future__ import annotations
import secrets
import time


class DistributedLockManager:
    def __init__(self, *, default_ttl: int = 30):
        self._locks: dict[str, dict] = {}
        self._default_ttl = default_ttl

    def acquire(self, key: str, *, owner: str, ttl: int | None = None,
                now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        ttl = ttl or self._default_ttl
        existing = self._locks.get(key)
        if existing and ts < existing["expires"]:
            if existing["owner"] == owner:
                existing["expires"] = ts + ttl  # renew
                return {"acquired": True, "renewed": True, "key": key, "token": existing["token"]}
            return {"acquired": False, "reason": "locked", "owner": existing["owner"],
                    "expires_in": round(existing["expires"] - ts, 1)}
        token = secrets.token_hex(8)
        self._locks[key] = {"owner": owner, "token": token, "acquired_at": ts, "expires": ts + ttl}
        return {"acquired": True, "renewed": False, "key": key, "token": token, "ttl": ttl}

    def release(self, key: str, *, token: str) -> dict:
        lock = self._locks.get(key)
        if not lock:
            return {"released": False, "reason": "not_found"}
        if lock["token"] != token:
            return {"released": False, "reason": "token_mismatch"}
        del self._locks[key]
        return {"released": True, "key": key}

    def status(self) -> dict:
        return {"active_locks": len(self._locks),
                "locks": [{"key": k, "owner": v["owner"]} for k, v in self._locks.items()]}
