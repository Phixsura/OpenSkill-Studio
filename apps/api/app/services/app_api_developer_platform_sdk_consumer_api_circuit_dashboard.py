"""Endpoint Circuit Breaker Dashboard — circuit breaker state overview."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()

STATES = ("closed", "open", "half_open")


@dataclass
class CircuitBreaker:
    circuit_id: str
    endpoint_id: str
    state: str = "closed"
    failure_count: int = 0
    success_count: int = 0
    failure_threshold: int = 5
    recovery_timeout_ms: int = 30000
    half_open_max: int = 3
    last_failure_at: str = ""
    last_state_change: str = ""
    total_trips: int = 0


@dataclass
class CircuitDashboard:
    """Monitor all circuit breakers across endpoints."""

    _circuits: dict[str, CircuitBreaker] = field(default_factory=dict)

    def register(self, cb: CircuitBreaker) -> dict:
        if cb.circuit_id in self._circuits:
            raise ValueError(f"Circuit {cb.circuit_id} already registered")
        self._circuits[cb.circuit_id] = cb
        logger.info("circuit_registered", circuit_id=cb.circuit_id)
        return {"circuit_id": cb.circuit_id, "endpoint_id": cb.endpoint_id}

    def record_success(self, circuit_id: str) -> dict:
        cb = self._circuits.get(circuit_id)
        if not cb:
            raise ValueError(f"Circuit {circuit_id} not found")
        if cb.state == "half_open":
            cb.success_count += 1
            if cb.success_count >= cb.half_open_max:
                cb.state = "closed"
                cb.failure_count = 0
                cb.success_count = 0
                logger.info("circuit_closed", circuit_id=circuit_id)
        elif cb.state == "closed":
            cb.failure_count = max(0, cb.failure_count - 1)
        return {"circuit_id": circuit_id, "state": cb.state}

    def record_failure(self, circuit_id: str, timestamp: str = "") -> dict:
        cb = self._circuits.get(circuit_id)
        if not cb:
            raise ValueError(f"Circuit {circuit_id} not found")
        cb.last_failure_at = timestamp
        if cb.state == "half_open":
            cb.state = "open"
            cb.success_count = 0
            cb.total_trips += 1
            logger.info("circuit_reopened", circuit_id=circuit_id)
        elif cb.state == "closed":
            cb.failure_count += 1
            if cb.failure_count >= cb.failure_threshold:
                cb.state = "open"
                cb.total_trips += 1
                logger.info("circuit_tripped", circuit_id=circuit_id)
        return {"circuit_id": circuit_id, "state": cb.state, "failures": cb.failure_count}

    def attempt_reset(self, circuit_id: str) -> dict:
        cb = self._circuits.get(circuit_id)
        if not cb:
            raise ValueError(f"Circuit {circuit_id} not found")
        if cb.state != "open":
            return {"error": "not_open"}
        cb.state = "half_open"
        cb.success_count = 0
        return {"circuit_id": circuit_id, "state": "half_open"}

    def force_close(self, circuit_id: str) -> dict:
        cb = self._circuits.get(circuit_id)
        if not cb:
            raise ValueError(f"Circuit {circuit_id} not found")
        cb.state = "closed"
        cb.failure_count = 0
        cb.success_count = 0
        return {"circuit_id": circuit_id, "state": "closed", "forced": True}

    def get_overview(self) -> dict:
        circuits = list(self._circuits.values())
        return {
            "total": len(circuits),
            "closed": sum(1 for c in circuits if c.state == "closed"),
            "open": sum(1 for c in circuits if c.state == "open"),
            "half_open": sum(1 for c in circuits if c.state == "half_open"),
            "total_trips": sum(c.total_trips for c in circuits),
        }

    def list_circuits(self, state: str | None = None) -> list[dict]:
        circuits = list(self._circuits.values())
        if state:
            circuits = [c for c in circuits if c.state == state]
        return [
            {"circuit_id": c.circuit_id, "endpoint_id": c.endpoint_id,
             "state": c.state, "failures": c.failure_count, "trips": c.total_trips}
            for c in circuits
        ]

    def get_circuit(self, circuit_id: str) -> dict | None:
        cb = self._circuits.get(circuit_id)
        if not cb:
            return None
        return {
            "circuit_id": cb.circuit_id, "endpoint_id": cb.endpoint_id,
            "state": cb.state, "failure_count": cb.failure_count,
            "threshold": cb.failure_threshold, "total_trips": cb.total_trips,
            "recovery_timeout_ms": cb.recovery_timeout_ms,
        }
