"""Idempotency key manager — ensure exactly-once request processing."""
from __future__ import annotations
import time


class IdempotencyManager:
    def __init__(self, ttl_seconds: int = 86400):
        self._keys: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def check_or_create(self, key: str, now: float | None = None) -> dict:
        now = now or time.time()
        self._cleanup(now)
        if key in self._keys:
            entry = self._keys[key]
            return {"duplicate": True, "key": key, "original_response": entry["response"],
                    "created_at": entry["created_at"]}
        self._keys[key] = {"created_at": now, "response": None, "expires_at": now + self._ttl}
        return {"duplicate": False, "key": key}

    def store_response(self, key: str, response: dict) -> dict:
        if key in self._keys:
            self._keys[key]["response"] = response
            return {"stored": True, "key": key}
        return {"stored": False, "reason": "key_not_found"}

    def _cleanup(self, now: float) -> None:
        expired = [k for k, v in self._keys.items() if v["expires_at"] <= now]
        for k in expired:
            del self._keys[k]

    def stats(self) -> dict:
        return {"active_keys": len(self._keys), "ttl_seconds": self._ttl}
