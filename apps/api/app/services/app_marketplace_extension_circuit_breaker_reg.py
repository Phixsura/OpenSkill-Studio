"""Circuit Breaker Registry — per-endpoint circuit breakers with half-open probing.

States: CLOSED → OPEN → HALF_OPEN → CLOSED (on success) or OPEN (on failure)
- CLOSED: requests flow normally, failures counted
- OPEN: requests immediately rejected, wait for recovery timeout
- HALF_OPEN: one probe request allowed; success closes, failure reopens
"""
from __future__ import annotations
from dataclasses import dataclass
import time
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    endpoint: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    success_threshold: int = 3  # successes needed in half-open to close
    recovery_timeout: float = 30.0  # seconds before half-open
    last_failure_time: float = 0.0
    last_state_change: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    total_short_circuits: int = 0

    def __post_init__(self):
        if not self.last_state_change:
            self.last_state_change = time.time()


class CircuitBreakerRegService:
    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}

    def register(self, endpoint: str, failure_threshold: int = 5,
                 success_threshold: int = 3, recovery_timeout: float = 30.0) -> CircuitBreaker:
        cb = CircuitBreaker(endpoint=endpoint, failure_threshold=failure_threshold,
                            success_threshold=success_threshold,
                            recovery_timeout=recovery_timeout)
        self._breakers[endpoint] = cb
        return cb

    def can_execute(self, endpoint: str) -> tuple[bool, str]:
        cb = self._breakers.get(endpoint)
        if not cb:
            return True, "no breaker registered"

        now = time.time()
        cb.total_requests += 1

        if cb.state == CircuitState.CLOSED:
            return True, "circuit closed"

        if cb.state == CircuitState.OPEN:
            elapsed = now - cb.last_failure_time
            if elapsed >= cb.recovery_timeout:
                # Transition to half-open
                cb.state = CircuitState.HALF_OPEN
                cb.success_count = 0
                cb.last_state_change = now
                return True, "circuit half-open (probe)"
            cb.total_short_circuits += 1
            retry_after = round(cb.recovery_timeout - elapsed, 1)
            return False, f"circuit open (retry in {retry_after}s)"

        if cb.state == CircuitState.HALF_OPEN:
            # Only allow one concurrent probe in half-open
            # (simplified: always allow in this in-memory version)
            return True, "circuit half-open (probe)"

        return True, "unknown state"

    def record_success(self, endpoint: str) -> CircuitState:
        cb = self._breakers.get(endpoint)
        if not cb:
            return CircuitState.CLOSED

        if cb.state == CircuitState.HALF_OPEN:
            cb.success_count += 1
            if cb.success_count >= cb.success_threshold:
                cb.state = CircuitState.CLOSED
                cb.failure_count = 0
                cb.last_state_change = time.time()
        elif cb.state == CircuitState.CLOSED:
            # Reset failure count on success
            cb.failure_count = 0

        return cb.state

    def record_failure(self, endpoint: str) -> CircuitState:
        cb = self._breakers.get(endpoint)
        if not cb:
            return CircuitState.CLOSED

        now = time.time()
        cb.total_failures += 1
        cb.last_failure_time = now

        if cb.state == CircuitState.HALF_OPEN:
            # Probe failed — back to open
            cb.state = CircuitState.OPEN
            cb.last_state_change = now
        elif cb.state == CircuitState.CLOSED:
            cb.failure_count += 1
            if cb.failure_count >= cb.failure_threshold:
                cb.state = CircuitState.OPEN
                cb.last_state_change = now

        return cb.state

    def get_all(self) -> list[CircuitBreaker]:
        return list(self._breakers.values())

    def get_stats(self, endpoint: str) -> dict | None:
        cb = self._breakers.get(endpoint)
        if not cb:
            return None
        return {
            "endpoint": cb.endpoint,
            "state": cb.state.value,
            "failure_count": cb.failure_count,
            "total_requests": cb.total_requests,
            "total_failures": cb.total_failures,
            "total_short_circuits": cb.total_short_circuits,
            "failure_rate": round(cb.total_failures / max(1, cb.total_requests) * 100, 1),
        }
