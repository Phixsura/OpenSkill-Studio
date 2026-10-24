"""Event deduplication engine — deduplicate events using idempotency keys."""
from __future__ import annotations
import hashlib


class EventDedup:
    def __init__(self, window_size: int = 10000):
        self._seen: dict[str, bool] = {}
        self._window = window_size
        self._deduped = 0

    def check(self, event_id: str, payload: str = "") -> dict:
        key = event_id or hashlib.sha256(payload.encode()).hexdigest()[:16]
        if key in self._seen:
            self._deduped += 1
            return {"duplicate": True, "key": key}
        self._seen[key] = True
        if len(self._seen) > self._window:
            oldest = next(iter(self._seen))
            del self._seen[oldest]
        return {"duplicate": False, "key": key}

    def stats(self) -> dict:
        return {"seen": len(self._seen), "deduped": self._deduped, "window": self._window}
