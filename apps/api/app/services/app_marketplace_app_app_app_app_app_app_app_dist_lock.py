"""Distributed lock manager — in-memory distributed locking."""
from __future__ import annotations
import time, secrets


class DistributedLockManager:
    def __init__(self, default_ttl: int = 30):
        self._locks: dict[str, dict] = {}
        self._ttl = default_ttl

    def acquire(self, resource: str, owner: str, ttl: int | None = None) -> dict:
        now = time.time()
        self._cleanup(now)
        if resource in self._locks:
            lock = self._locks[resource]
            if lock["owner"] != owner:
                return {"acquired": False, "owner": lock["owner"],
                        "expires_in": round(lock["expires_at"] - now, 1)}
        token = secrets.token_hex(8)
        self._locks[resource] = {"owner": owner, "token": token,
                                  "acquired_at": now,
                                  "expires_at": now + (ttl or self._ttl)}
        return {"acquired": True, "token": token, "resource": resource}

    def release(self, resource: str, token: str) -> dict:
        lock = self._locks.get(resource)
        if not lock or lock["token"] != token:
            return {"released": False, "reason": "invalid_token"}
        del self._locks[resource]
        return {"released": True, "resource": resource}

    def _cleanup(self, now: float) -> None:
        expired = [r for r, l in self._locks.items() if l["expires_at"] <= now]
        for r in expired:
            del self._locks[r]

    def status(self) -> dict:
        self._cleanup(time.time())
        return {"active_locks": len(self._locks), "default_ttl": self._ttl}
