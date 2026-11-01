"""API Consumer Circuit State Manager — manage circuit breaker state transitions."""
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
class CircuitInfo:
    consumer_id: str
    endpoint: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_transition: float = field(default_factory=time.time)
    total_transitions: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiCircuitStateManager:
    def __init__(self, failure_threshold: int = 5, recovery_s: int = 30) -> None:
        self._circuits: dict[tuple[str, str, str], CircuitInfo] = {}
        self._threshold = max(1, failure_threshold)
        self._recovery = max(0, recovery_s)

    def get_or_create(self, installation_id: str, consumer_id: str, endpoint: str) -> CircuitInfo:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id, endpoint)
        if key not in self._circuits:
            self._circuits[key] = CircuitInfo(consumer_id=consumer_id, endpoint=endpoint)
        return self._circuits[key]

    def record_success(self, installation_id: str, consumer_id: str, endpoint: str) -> CircuitInfo:
        c = self.get_or_create(installation_id, consumer_id, endpoint)
        c.success_count += 1
        c.failure_count = 0
        if c.state == CircuitState.HALF_OPEN:
            c.state = CircuitState.CLOSED
            c.total_transitions += 1
            c.last_transition = time.time()
        return c

    def record_failure(self, installation_id: str, consumer_id: str, endpoint: str) -> CircuitInfo:
        c = self.get_or_create(installation_id, consumer_id, endpoint)
        c.failure_count += 1
        if c.state == CircuitState.CLOSED and c.failure_count >= self._threshold:
            c.state = CircuitState.OPEN
            c.total_transitions += 1
            c.last_transition = time.time()
        elif c.state == CircuitState.HALF_OPEN:
            c.state = CircuitState.OPEN
            c.total_transitions += 1
            c.last_transition = time.time()
        return c

    def is_allowed(self, installation_id: str, consumer_id: str, endpoint: str) -> bool:
        c = self._circuits.get((installation_id, consumer_id, endpoint))
        if c is None: return True
        if c.state == CircuitState.CLOSED: return True
        if c.state == CircuitState.OPEN and time.time() - c.last_transition >= self._recovery:
            c.state = CircuitState.HALF_OPEN
            return True
        return c.state == CircuitState.HALF_OPEN

    def open_circuits(self, installation_id: str) -> list[CircuitInfo]:
        return [c for (inst, _, _), c in self._circuits.items() if inst == installation_id and c.state == CircuitState.OPEN]
