"""Connection pool — database connection pool monitoring."""

from __future__ import annotations
from datetime import datetime, timezone


class ConnectionPoolStats:
    def __init__(self, *, min_size: int = 5, max_size: int = 20):
        self.min_size = min_size
        self.max_size = max_size
        self.active = 0
        self.idle = min_size
        self.waiting = 0
        self.total_acquired = 0
        self.total_released = 0

    def acquire(self) -> dict:
        if self.idle > 0:
            self.idle -= 1
            self.active += 1
            self.total_acquired += 1
            return {"acquired": True, "waited": False}
        if self.active < self.max_size:
            self.active += 1
            self.total_acquired += 1
            return {"acquired": True, "waited": False}
        self.waiting += 1
        return {"acquired": False, "waited": True, "queue_position": self.waiting}

    def release(self) -> dict:
        if self.active <= 0:
            return {"released": False, "error": "No active connections"}
        self.active -= 1
        if self.waiting > 0:
            self.waiting -= 1
            self.active += 1
        else:
            self.idle += 1
        self.total_released += 1
        return {"released": True}

    def stats(self) -> dict:
        total = self.active + self.idle
        utilization = round(self.active / max(self.max_size, 1) * 100, 1)
        return {"active": self.active, "idle": self.idle, "waiting": self.waiting,
                "total": total, "max_size": self.max_size,
                "utilization_pct": utilization,
                "healthy": utilization < 90 and self.waiting == 0}
