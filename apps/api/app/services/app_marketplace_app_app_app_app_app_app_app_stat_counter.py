"""Stat counter — atomic counter operations for platform metrics."""
from __future__ import annotations


class StatCounter:
    def __init__(self):
        self._counters: dict[str, int] = {}

    def increment(self, key: str, *, by: int = 1) -> dict:
        self._counters[key] = self._counters.get(key, 0) + by
        return {"key": key, "value": self._counters[key]}

    def decrement(self, key: str, *, by: int = 1) -> dict:
        self._counters[key] = self._counters.get(key, 0) - by
        return {"key": key, "value": self._counters[key]}

    def get(self, key: str) -> int:
        return self._counters.get(key, 0)

    def reset(self, key: str) -> dict:
        old = self._counters.pop(key, 0)
        return {"key": key, "old_value": old, "reset": True}

    def all(self) -> dict[str, int]:
        return dict(self._counters)

    def summary(self) -> dict:
        total = sum(self._counters.values())
        return {"counters": len(self._counters), "total": total,
                "top": max(self._counters.items(), key=lambda x: x[1]) if self._counters else None}
