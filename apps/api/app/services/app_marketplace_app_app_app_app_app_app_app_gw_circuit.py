"""API gateway circuit breaker — protect downstream services."""
from __future__ import annotations
import time


class GatewayCircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_seconds: int = 30):
        self._threshold = failure_threshold
        self._recovery = recovery_seconds
        self._circuits: dict[str, dict] = {}

    def _get(self, service: str) -> dict:
        if service not in self._circuits:
            self._circuits[service] = {"state": "closed", "failures": 0, "opened_at": 0}
        return self._circuits[service]

    def record_success(self, service: str) -> dict:
        c = self._get(service)
        c["failures"] = 0
        c["state"] = "closed"
        return {"service": service, "state": "closed"}

    def record_failure(self, service: str, now: float | None = None) -> dict:
        now = now or time.time()
        c = self._get(service)
        c["failures"] += 1
        if c["failures"] >= self._threshold:
            c["state"] = "open"
            c["opened_at"] = now
        return {"service": service, "state": c["state"], "failures": c["failures"]}

    def can_pass(self, service: str, now: float | None = None) -> dict:
        now = now or time.time()
        c = self._get(service)
        if c["state"] == "closed":
            return {"allowed": True, "state": "closed"}
        elapsed = now - c["opened_at"]
        if elapsed >= self._recovery:
            c["state"] = "half-open"
            return {"allowed": True, "state": "half-open"}
        return {"allowed": False, "state": "open", "retry_after": round(self._recovery - elapsed, 1)}

    def summary(self) -> dict:
        open_count = sum(1 for c in self._circuits.values() if c["state"] == "open")
        return {"total": len(self._circuits), "open": open_count,
                "closed": len(self._circuits) - open_count}
