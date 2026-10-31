"""App API Developer Circuit Breaker Dashboard — monitor circuit breaker states."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class CircuitState:
    endpoint: str
    state: str = "closed"  # "closed", "open", "half_open"
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: float = 0.0
    opened_at: float = 0.0
    failure_threshold: int = 5
    recovery_timeout_s: int = 60

    @property
    def failure_rate(self) -> float:
        total = self.failure_count + self.success_count
        return round(self.failure_count / total * 100, 1) if total > 0 else 0.0

class AppAPIDeveloperAPICircuitBreakerDashboard:
    def __init__(self) -> None:
        self._circuits: dict[tuple[str, str], CircuitState] = {}

    def register(self, installation_id: str, endpoint: str, failure_threshold: int = 5, recovery_timeout_s: int = 60) -> CircuitState:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, endpoint)
        c = CircuitState(endpoint=endpoint, failure_threshold=failure_threshold, recovery_timeout_s=recovery_timeout_s)
        self._circuits[key] = c
        return c

    def record_success(self, installation_id: str, endpoint: str) -> CircuitState:
        c = self._get(installation_id, endpoint)
        c.success_count += 1
        if c.state == "half_open":
            c.state = "closed"
            c.failure_count = 0
        return c

    def record_failure(self, installation_id: str, endpoint: str) -> CircuitState:
        c = self._get(installation_id, endpoint)
        c.failure_count += 1
        c.last_failure_at = time.time()
        if c.failure_count >= c.failure_threshold and c.state == "closed":
            c.state = "open"
            c.opened_at = time.time()
        return c

    def check_state(self, installation_id: str, endpoint: str) -> str:
        c = self._get(installation_id, endpoint)
        if c.state == "open" and time.time() - c.opened_at >= c.recovery_timeout_s:
            c.state = "half_open"
        return c.state

    def open_circuits(self, installation_id: str) -> list[CircuitState]:
        return [c for (inst, _), c in self._circuits.items() if inst == installation_id and c.state in ("open", "half_open")]

    def all_circuits(self, installation_id: str) -> list[CircuitState]:
        return [c for (inst, _), c in self._circuits.items() if inst == installation_id]

    def _get(self, installation_id: str, endpoint: str) -> CircuitState:
        key = (installation_id, endpoint)
        c = self._circuits.get(key)
        if c is None: raise KeyError(f"Circuit for {endpoint} not found")
        return c
