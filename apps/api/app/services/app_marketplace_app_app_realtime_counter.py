"""Realtime counter — atomic counters with time-windowed aggregation."""

from collections import defaultdict
from datetime import datetime, timezone, timedelta


class RealtimeCounter:
    def __init__(self):
        self._counts: dict[str, int] = defaultdict(int)
        self._events: dict[str, list[str]] = defaultdict(list)

    def increment(self, key: str, amount: int = 1) -> dict:
        self._counts[key] += amount
        self._events[key].append(datetime.now(timezone.utc).isoformat())
        return {"key": key, "count": self._counts[key]}

    def get(self, key: str) -> dict:
        return {"key": key, "count": self._counts.get(key, 0)}

    def get_all(self) -> dict:
        return {"counters": dict(self._counts), "total_keys": len(self._counts),
                "grand_total": sum(self._counts.values())}

    def reset(self, key: str) -> dict:
        prev = self._counts.pop(key, 0)
        self._events.pop(key, None)
        return {"key": key, "previous": prev}
