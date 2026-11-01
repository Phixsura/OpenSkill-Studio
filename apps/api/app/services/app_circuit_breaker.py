"""App Circuit Breaker — protect services from cascading failures.

Implements circuit breaker pattern:
- Closed → Open on failure threshold
- Open → Half-open after cooldown
- Half-open → Closed on success, Open on failure
- Per-installation scoped breakers
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class BreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreaker:
    """A circuit breaker for a service."""

    breaker_id: str
    service_name: str
    failure_threshold: int = 5
    cooldown_seconds: float = 30.0
    state: BreakerState = BreakerState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: float | None = None
    opened_at: float | None = None

    def should_allow(self) -> bool:
        if self.state == BreakerState.CLOSED:
            return True
        if self.state == BreakerState.OPEN:
            if self.opened_at and (time.time() - self.opened_at) >= self.cooldown_seconds:
                self.state = BreakerState.HALF_OPEN
                return True
            return False
        # half_open: allow one request
        return True


class AppCircuitBreaker:
    """Manage circuit breakers for services."""

    def __init__(self) -> None:
        self._breakers: dict[tuple[str, str], CircuitBreaker] = {}

    def create(
        self, installation_id: str, breaker_id: str, service_name: str,
        failure_threshold: int = 5, cooldown_seconds: float = 30.0,
    ) -> CircuitBreaker:
        if not installation_id:
            raise ValueError("installation_id is required")
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least 1")

        cb = CircuitBreaker(
            breaker_id=breaker_id, service_name=service_name,
            failure_threshold=failure_threshold, cooldown_seconds=cooldown_seconds,
        )
        self._breakers[(installation_id, breaker_id)] = cb
        return cb

    def record_success(self, installation_id: str, breaker_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, breaker_id)
        cb.success_count += 1
        if cb.state == BreakerState.HALF_OPEN:
            cb.state = BreakerState.CLOSED
            cb.failure_count = 0
        return cb

    def record_failure(self, installation_id: str, breaker_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, breaker_id)
        cb.failure_count += 1
        cb.last_failure_at = time.time()
        if cb.state == BreakerState.HALF_OPEN:
            cb.state = BreakerState.OPEN
            cb.opened_at = time.time()
        elif cb.failure_count >= cb.failure_threshold:
            cb.state = BreakerState.OPEN
            cb.opened_at = time.time()
        return cb

    def is_allowed(self, installation_id: str, breaker_id: str) -> bool:
        return self._get(installation_id, breaker_id).should_allow()

    def reset(self, installation_id: str, breaker_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, breaker_id)
        cb.state = BreakerState.CLOSED
        cb.failure_count = 0
        return cb

    def get_state(self, installation_id: str, breaker_id: str) -> BreakerState:
        return self._get(installation_id, breaker_id).state

    def list_breakers(self, installation_id: str) -> list[CircuitBreaker]:
        return [cb for (inst, _), cb in self._breakers.items() if inst == installation_id]

    def open_breakers(self, installation_id: str) -> list[CircuitBreaker]:
        return [
            cb for (inst, _), cb in self._breakers.items()
            if inst == installation_id and cb.state == BreakerState.OPEN
        ]

    def _get(self, installation_id: str, breaker_id: str) -> CircuitBreaker:
        key = (installation_id, breaker_id)
        cb = self._breakers.get(key)
        if cb is None:
            raise KeyError(f"Breaker {breaker_id} not found")
        return cb
