"""API Webhook Circuit Breaker — protect webhook consumers with circuit breaker pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import time
import structlog

log = structlog.get_logger()

class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

@dataclass
class CircuitBreaker:
    consumer_id: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    recovery_timeout_s: int = 60
    half_open_max: int = 3
    last_failure_at: float = 0.0
    opened_at: float = 0.0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiWebhookCircuitBreaker:
    def __init__(self) -> None:
        self._breakers: dict[tuple[str, str], CircuitBreaker] = {}

    def get_or_create(self, installation_id: str, consumer_id: str, failure_threshold: int = 5, recovery_timeout_s: int = 60) -> CircuitBreaker:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        if key not in self._breakers:
            self._breakers[key] = CircuitBreaker(consumer_id=consumer_id, failure_threshold=failure_threshold, recovery_timeout_s=recovery_timeout_s)
        return self._breakers[key]

    def should_allow(self, installation_id: str, consumer_id: str) -> bool:
        cb = self._breakers.get((installation_id, consumer_id))
        if cb is None: return True
        if cb.state == CircuitState.CLOSED: return True
        if cb.state == CircuitState.OPEN:
            if time.time() - cb.opened_at >= cb.recovery_timeout_s:
                cb.state = CircuitState.HALF_OPEN
                cb.success_count = 0
                return True
            return False
        # half_open
        return cb.success_count < cb.half_open_max

    def record_success(self, installation_id: str, consumer_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, consumer_id)
        cb.success_count += 1
        if cb.state == CircuitState.HALF_OPEN and cb.success_count >= cb.half_open_max:
            cb.state = CircuitState.CLOSED
            cb.failure_count = 0
        return cb

    def record_failure(self, installation_id: str, consumer_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, consumer_id)
        cb.failure_count += 1
        cb.last_failure_at = time.time()
        if cb.state == CircuitState.HALF_OPEN:
            cb.state = CircuitState.OPEN
            cb.opened_at = time.time()
        elif cb.state == CircuitState.CLOSED and cb.failure_count >= cb.failure_threshold:
            cb.state = CircuitState.OPEN
            cb.opened_at = time.time()
        return cb

    def reset(self, installation_id: str, consumer_id: str) -> CircuitBreaker:
        cb = self._get(installation_id, consumer_id)
        cb.state = CircuitState.CLOSED
        cb.failure_count = 0
        cb.success_count = 0
        return cb

    def list_open(self, installation_id: str) -> list[CircuitBreaker]:
        return [cb for (inst, _), cb in self._breakers.items() if inst == installation_id and cb.state == CircuitState.OPEN]

    def _get(self, installation_id: str, consumer_id: str) -> CircuitBreaker:
        cb = self._breakers.get((installation_id, consumer_id))
        if cb is None: raise KeyError(f"No breaker for {consumer_id}")
        return cb
