"""Request concurrency limiter — limit concurrent requests per service."""
from __future__ import annotations


class ConcurrencyLimiter:
    def __init__(self):
        self._limits: dict[str, int] = {}
        self._active: dict[str, int] = {}
        self._rejected = 0

    def set_limit(self, service: str, max_concurrent: int) -> dict:
        self._limits[service] = max_concurrent
        self._active.setdefault(service, 0)
        return {"service": service, "max_concurrent": max_concurrent}

    def acquire(self, service: str) -> dict:
        limit = self._limits.get(service, 100)
        current = self._active.get(service, 0)
        if current >= limit:
            self._rejected += 1
            return {"acquired": False, "service": service, "reason": "at_limit",
                    "current": current, "limit": limit}
        self._active[service] = current + 1
        return {"acquired": True, "service": service,
                "current": current + 1, "limit": limit}

    def release(self, service: str) -> dict:
        current = self._active.get(service, 0)
        self._active[service] = max(0, current - 1)
        return {"service": service, "current": self._active[service]}

    def stats(self) -> dict:
        return {"services": len(self._limits), "rejected": self._rejected,
                "active": dict(self._active)}
