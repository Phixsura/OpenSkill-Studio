"""Circuit breaker — fault tolerance pattern for external service calls."""

from __future__ import annotations
import time

STATES = ("closed", "open", "half_open")


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, recovery_timeout_s: float = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_s = recovery_timeout_s
        self.failures = 0
        self.state = "closed"
        self._opened_at: float | None = None

    def record_success(self, now: float | None = None) -> dict:
        self.failures = 0
        if self.state == "half_open":
            self.state = "closed"
        return {"state": self.state, "failures": self.failures}

    def record_failure(self, now: float | None = None) -> dict:
        t = now if now is not None else time.monotonic()
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.state = "open"
            self._opened_at = t
        return {"state": self.state, "failures": self.failures}

    def can_execute(self, now: float | None = None) -> dict:
        t = now if now is not None else time.monotonic()
        if self.state == "closed":
            return {"allowed": True, "state": self.state}
        if self.state == "open" and self._opened_at is not None:
            if t - self._opened_at >= self.recovery_timeout_s:
                self.state = "half_open"
                return {"allowed": True, "state": "half_open"}
        return {"allowed": self.state == "half_open", "state": self.state}

    def stats(self) -> dict:
        return {"state": self.state, "failures": self.failures,
                "threshold": self.failure_threshold,
                "recovery_timeout_s": self.recovery_timeout_s}
