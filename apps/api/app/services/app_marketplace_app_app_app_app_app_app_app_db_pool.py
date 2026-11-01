"""Database connection pooler — manage and monitor connection pools."""
from __future__ import annotations


class ConnectionPool:
    def __init__(self, *, max_size: int = 20, min_size: int = 5):
        self.max_size = max_size
        self.min_size = min_size
        self._active = 0
        self._idle = min_size
        self._total_acquired = 0
        self._total_released = 0
        self._waits = 0

    def acquire(self) -> dict:
        self._total_acquired += 1
        if self._idle > 0:
            self._idle -= 1
            self._active += 1
            return {"acquired": True, "waited": False, "active": self._active, "idle": self._idle}
        if self._active < self.max_size:
            self._active += 1
            return {"acquired": True, "waited": False, "active": self._active, "idle": self._idle}
        self._waits += 1
        return {"acquired": False, "waited": True, "reason": "pool_exhausted",
                "active": self._active}

    def release(self) -> dict:
        if self._active <= 0:
            return {"error": "No active connections to release"}
        self._active -= 1
        self._idle += 1
        self._total_released += 1
        return {"released": True, "active": self._active, "idle": self._idle}

    def stats(self) -> dict:
        total = self._active + self._idle
        utilization = round(self._active / max(self.max_size, 1) * 100, 1)
        return {
            "max_size": self.max_size, "active": self._active, "idle": self._idle,
            "total": total, "utilization": utilization,
            "utilization_display": f"{utilization}%",
            "total_acquired": self._total_acquired,
            "total_released": self._total_released,
            "waits": self._waits,
            "health": "saturated" if utilization > 90 else "busy" if utilization > 70 else "healthy",
        }
