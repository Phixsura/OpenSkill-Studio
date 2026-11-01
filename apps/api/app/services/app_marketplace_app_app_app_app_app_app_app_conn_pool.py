"""Connection pool manager — manage database/service connection pools."""
from __future__ import annotations


class ConnectionPool:
    def __init__(self, name: str, max_size: int = 20, min_size: int = 5):
        self.name = name
        self.max_size = max_size
        self.min_size = min_size
        self._active = 0
        self._idle = min_size
        self._total_acquired = 0
        self._total_released = 0
        self._wait_count = 0

    def acquire(self) -> dict:
        self._total_acquired += 1
        if self._idle > 0:
            self._idle -= 1
            self._active += 1
            return {"acquired": True, "wait": False, "active": self._active}
        if self._active < self.max_size:
            self._active += 1
            return {"acquired": True, "wait": False, "active": self._active}
        self._wait_count += 1
        return {"acquired": False, "wait": True, "reason": "pool_exhausted"}

    def release(self) -> dict:
        if self._active > 0:
            self._active -= 1
            self._idle += 1
            self._total_released += 1
        return {"active": self._active, "idle": self._idle}

    def stats(self) -> dict:
        utilization = round(self._active / max(self.max_size, 1) * 100, 1)
        return {"name": self.name, "active": self._active, "idle": self._idle,
                "max_size": self.max_size, "utilization_pct": utilization,
                "total_acquired": self._total_acquired,
                "waits": self._wait_count}
