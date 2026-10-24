"""Health check scheduler — schedule and track periodic health checks."""
from __future__ import annotations
import time


class HealthCheckScheduler:
    def __init__(self):
        self._checks: dict[str, dict] = {}

    def register(self, name: str, interval_seconds: int, url: str) -> dict:
        self._checks[name] = {"name": name, "interval": interval_seconds, "url": url,
                                "last_check": 0, "last_status": "pending",
                                "consecutive_failures": 0, "total_checks": 0}
        return self._checks[name]

    def record_result(self, name: str, healthy: bool) -> dict:
        c = self._checks[name]
        c["total_checks"] += 1
        c["last_check"] = time.time()
        if healthy:
            c["last_status"] = "healthy"
            c["consecutive_failures"] = 0
        else:
            c["consecutive_failures"] += 1
            c["last_status"] = "unhealthy"
        return {"name": name, "status": c["last_status"],
                "consecutive_failures": c["consecutive_failures"]}

    def due_checks(self, now: float | None = None) -> list[dict]:
        now = now or time.time()
        due = []
        for c in self._checks.values():
            if now - c["last_check"] >= c["interval"]:
                due.append({"name": c["name"], "url": c["url"]})
        return due

    def stats(self) -> dict:
        unhealthy = sum(1 for c in self._checks.values() if c["last_status"] == "unhealthy")
        return {"total": len(self._checks), "unhealthy": unhealthy,
                "healthy": len(self._checks) - unhealthy}
