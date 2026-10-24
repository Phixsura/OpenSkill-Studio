"""Idempotent request handler — handle idempotent writes with stored results."""
from __future__ import annotations
import hashlib, time


class IdempotentHandler:
    def __init__(self, ttl_seconds: int = 86400):
        self._results: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def handle(self, idempotency_key: str, handler: callable) -> dict:
        if idempotency_key in self._results:
            entry = self._results[idempotency_key]
            return {"cached": True, "result": entry["result"]}
        result = handler()
        self._results[idempotency_key] = {"result": result, "stored_at": time.time()}
        return {"cached": False, "result": result}

    def cleanup(self, now: float | None = None) -> dict:
        now = now or time.time()
        before = len(self._results)
        self._results = {k: v for k, v in self._results.items()
                         if now - v["stored_at"] < self._ttl}
        return {"removed": before - len(self._results), "remaining": len(self._results)}

    def stats(self) -> dict:
        return {"stored_results": len(self._results), "ttl_seconds": self._ttl}
