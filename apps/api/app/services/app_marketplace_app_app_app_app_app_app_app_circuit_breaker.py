"""Circuit breaker — protect downstream services from cascading failures."""
from __future__ import annotations
import time


class CircuitBreaker:
    def __init__(self, *, failure_threshold: int = 5, recovery_timeout: float = 30,
                  half_open_max: int = 1):
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._half_open_max = half_open_max
        self._failures = 0
        self._successes = 0
        self._state = "closed"  # closed, open, half_open
        self._last_failure_time: float = 0
        self._half_open_calls = 0

    def call(self, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.monotonic()
        if self._state == "open":
            if ts - self._last_failure_time >= self._recovery_timeout:
                self._state = "half_open"
                self._half_open_calls = 0
            else:
                return {"allowed": False, "state": "open",
                        "retry_after": round(self._recovery_timeout - (ts - self._last_failure_time), 1)}
        if self._state == "half_open" and self._half_open_calls >= self._half_open_max:
            return {"allowed": False, "state": "half_open", "reason": "max_probes_reached"}
        if self._state == "half_open":
            self._half_open_calls += 1
        return {"allowed": True, "state": self._state}

    def record_success(self) -> dict:
        self._successes += 1
        if self._state == "half_open":
            self._state = "closed"
            self._failures = 0
        return {"state": self._state, "failures": self._failures}

    def record_failure(self, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.monotonic()
        self._failures += 1
        self._last_failure_time = ts
        if self._state == "half_open":
            self._state = "open"
        elif self._failures >= self._failure_threshold:
            self._state = "open"
        return {"state": self._state, "failures": self._failures}

    def status(self) -> dict:
        return {"state": self._state, "failures": self._failures,
                "successes": self._successes, "threshold": self._failure_threshold}
