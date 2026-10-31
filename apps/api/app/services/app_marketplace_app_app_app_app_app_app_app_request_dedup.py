"""Request deduplicator — idempotency key tracking to prevent duplicate processing."""
from __future__ import annotations
import time


class RequestDeduplicator:
    def __init__(self, *, ttl_sec: int = 3600):
        self._keys: dict[str, dict] = {}
        self._ttl = ttl_sec

    def check(self, idempotency_key: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        self._cleanup(ts)
        entry = self._keys.get(idempotency_key)
        if entry:
            return {"duplicate": True, "original_response": entry["response"],
                    "processed_at": entry["created"]}
        return {"duplicate": False}

    def record(self, idempotency_key: str, response: dict, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        self._keys[idempotency_key] = {"response": response, "created": ts}
        return {"recorded": True, "key": idempotency_key, "expires_in": self._ttl}

    def stats(self) -> dict:
        return {"tracked_keys": len(self._keys), "ttl_sec": self._ttl}

    def _cleanup(self, now: float) -> None:
        expired = [k for k, v in self._keys.items() if now - v["created"] > self._ttl]
        for k in expired:
            del self._keys[k]
