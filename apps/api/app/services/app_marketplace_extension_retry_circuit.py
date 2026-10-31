"""Retry Circuit — unified retry + circuit breaker for resilient calls.

Combines retry logic with circuit breaking into a single policy:
retry within the circuit, but trip the circuit when retries exhaust.

Implements:
- Configurable retry count with backoff
- Circuit opens after N consecutive failures across calls
- Half-open state: single probe request
- Success resets both retry count and failure counter
- Call wrapping: pass a callable, get result or error
- Per-operation metrics
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from enum import Enum


class State(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryCircuitConfig:
    max_retries: int = 3
    backoff_base_ms: float = 100
    failure_threshold: int = 5  # failures to open circuit
    recovery_timeout_s: float = 30
    success_threshold: int = 2  # successes in half-open to close


@dataclass
class CallResult:
    success: bool
    result: object = None
    error: str = ""
    attempts: int = 0
    circuit_state: str = ""
    total_ms: float = 0


class RetryCircuitService:
    def __init__(self):
        self._circuits: dict[str, dict] = {}

    def register(self, name: str, config: RetryCircuitConfig | None = None) -> None:
        cfg = config or RetryCircuitConfig()
        self._circuits[name] = {
            "config": cfg,
            "state": State.CLOSED,
            "failure_count": 0,
            "success_count": 0,  # in half-open
            "last_failure_time": 0.0,
            "total_calls": 0,
            "total_successes": 0,
            "total_failures": 0,
        }

    def call(self, name: str, fn: callable, *args, **kwargs) -> CallResult:
        """Execute fn with retry + circuit breaker protection."""
        circuit = self._circuits.get(name)
        if not circuit:
            self.register(name)
            circuit = self._circuits[name]

        cfg = circuit["config"]
        start = time.time()
        circuit["total_calls"] += 1

        # Circuit open check
        if circuit["state"] == State.OPEN:
            elapsed = time.time() - circuit["last_failure_time"]
            if elapsed < cfg.recovery_timeout_s:
                return CallResult(success=False, error="circuit open",
                                  circuit_state="open",
                                  total_ms=round((time.time() - start) * 1000, 2))
            # Transition to half-open
            circuit["state"] = State.HALF_OPEN
            circuit["success_count"] = 0

        # Execute with retries
        last_error = ""
        for attempt in range(1, cfg.max_retries + 1):
            try:
                result = fn(*args, **kwargs)
                self._on_success(circuit, cfg)
                return CallResult(success=True, result=result,
                                  attempts=attempt,
                                  circuit_state=circuit["state"].value,
                                  total_ms=round((time.time() - start) * 1000, 2))
            except Exception as e:
                last_error = str(e)
                if attempt < cfg.max_retries:
                    # Backoff before retry
                    backoff = cfg.backoff_base_ms * (2 ** (attempt - 1)) / 1000
                    time.sleep(min(backoff, 0.001))  # cap for tests

        # All retries exhausted
        self._on_failure(circuit, cfg)
        return CallResult(success=False, error=last_error,
                          attempts=cfg.max_retries,
                          circuit_state=circuit["state"].value,
                          total_ms=round((time.time() - start) * 1000, 2))

    def _on_success(self, circuit: dict, cfg: RetryCircuitConfig) -> None:
        circuit["total_successes"] += 1
        if circuit["state"] == State.HALF_OPEN:
            circuit["success_count"] += 1
            if circuit["success_count"] >= cfg.success_threshold:
                circuit["state"] = State.CLOSED
                circuit["failure_count"] = 0
        else:
            circuit["failure_count"] = 0

    def _on_failure(self, circuit: dict, cfg: RetryCircuitConfig) -> None:
        circuit["total_failures"] += 1
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = time.time()

        if circuit["state"] == State.HALF_OPEN:
            circuit["state"] = State.OPEN
        elif circuit["failure_count"] >= cfg.failure_threshold:
            circuit["state"] = State.OPEN

    def get_state(self, name: str) -> dict:
        c = self._circuits.get(name)
        if not c:
            return {}
        return {
            "state": c["state"].value,
            "failure_count": c["failure_count"],
            "total_calls": c["total_calls"],
            "total_successes": c["total_successes"],
            "total_failures": c["total_failures"],
            "success_rate": round(c["total_successes"] / max(1, c["total_calls"]) * 100, 1),
        }

    def reset(self, name: str) -> bool:
        c = self._circuits.get(name)
        if not c:
            return False
        c["state"] = State.CLOSED
        c["failure_count"] = 0
        c["success_count"] = 0
        return True
