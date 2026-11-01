"""Sandbox Circuit Breaker — circuit breaker pattern for sandbox operations.

Implements closed/open/half-open states with configurable failure
thresholds, cooldown periods, success-based recovery, and per-operation
circuit tracking.
"""
from __future__ import annotations
import time
from collections import defaultdict
from dataclasses import dataclass
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class Circuit:
    name: str
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    success_threshold: int = 2  # successes needed to close from half-open
    cooldown_seconds: float = 30.0
    last_failure_at: float = 0.0
    last_state_change: float = 0.0
    total_requests: int = 0
    total_failures: int = 0
    total_short_circuits: int = 0

    def __post_init__(self):
        self.last_state_change = time.time()


class SandboxCircuitBreakerService:
    """Circuit breaker for sandbox operations with recovery."""

    def __init__(self):
        self._circuits: dict[str, dict[str, Circuit]] = defaultdict(dict)

    def register(self, sandbox_id: str, name: str,
                 failure_threshold: int = 5,
                 success_threshold: int = 2,
                 cooldown_seconds: float = 30.0) -> Circuit:
        circuit = Circuit(
            name=name, failure_threshold=failure_threshold,
            success_threshold=success_threshold,
            cooldown_seconds=cooldown_seconds,
        )
        self._circuits[sandbox_id][name] = circuit
        return circuit

    def can_execute(self, sandbox_id: str, name: str) -> dict:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if not circuit:
            return {"allowed": True, "reason": "No circuit registered"}

        now = time.time()

        if circuit.state == CircuitState.CLOSED:
            return {"allowed": True, "state": "closed"}

        if circuit.state == CircuitState.OPEN:
            if now - circuit.last_failure_at >= circuit.cooldown_seconds:
                circuit.state = CircuitState.HALF_OPEN
                circuit.success_count = 0
                circuit.last_state_change = now
                return {"allowed": True, "state": "half_open"}
            circuit.total_short_circuits += 1
            remaining = round(circuit.cooldown_seconds - (now - circuit.last_failure_at), 1)
            return {"allowed": False, "state": "open",
                    "retry_after_seconds": remaining}

        # HALF_OPEN
        return {"allowed": True, "state": "half_open"}

    def record_success(self, sandbox_id: str, name: str) -> CircuitState:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if not circuit:
            return CircuitState.CLOSED

        circuit.total_requests += 1

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.success_count += 1
            if circuit.success_count >= circuit.success_threshold:
                circuit.state = CircuitState.CLOSED
                circuit.failure_count = 0
                circuit.last_state_change = time.time()

        elif circuit.state == CircuitState.CLOSED:
            circuit.failure_count = max(0, circuit.failure_count - 1)

        return circuit.state

    def record_failure(self, sandbox_id: str, name: str) -> CircuitState:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if not circuit:
            return CircuitState.CLOSED

        circuit.total_requests += 1
        circuit.total_failures += 1
        circuit.last_failure_at = time.time()

        if circuit.state == CircuitState.HALF_OPEN:
            circuit.state = CircuitState.OPEN
            circuit.last_state_change = time.time()

        elif circuit.state == CircuitState.CLOSED:
            circuit.failure_count += 1
            if circuit.failure_count >= circuit.failure_threshold:
                circuit.state = CircuitState.OPEN
                circuit.last_state_change = time.time()

        return circuit.state

    def force_open(self, sandbox_id: str, name: str) -> bool:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if circuit:
            circuit.state = CircuitState.OPEN
            circuit.last_failure_at = time.time()
            return True
        return False

    def force_close(self, sandbox_id: str, name: str) -> bool:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if circuit:
            circuit.state = CircuitState.CLOSED
            circuit.failure_count = 0
            return True
        return False

    def get_status(self, sandbox_id: str, name: str) -> dict | None:
        circuit = self._circuits.get(sandbox_id, {}).get(name)
        if not circuit:
            return None
        return {
            "name": circuit.name, "state": circuit.state.value,
            "failure_count": circuit.failure_count,
            "total_requests": circuit.total_requests,
            "total_failures": circuit.total_failures,
            "total_short_circuits": circuit.total_short_circuits,
            "failure_rate": round(circuit.total_failures / max(circuit.total_requests, 1) * 100, 1),
        }

    def list_circuits(self, sandbox_id: str) -> list[dict]:
        return [self.get_status(sandbox_id, name)
                for name in self._circuits.get(sandbox_id, {})]
