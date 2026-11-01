"""Endpoint Circuit Breaker — protect endpoints from cascading failures."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class CircuitBreakerConfig:
    endpoint_path: str
    failure_threshold: int = 5       # failures to trip
    success_threshold: int = 3       # successes to close from half-open
    timeout_seconds: int = 30        # how long to stay open before half-open

@dataclass
class CircuitState:
    endpoint_path: str
    state: str = "closed"  # "closed", "open", "half_open"
    failure_count: int = 0
    success_count: int = 0
    last_failure_at: datetime | None = None
    opened_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiEndpointCircuitBreaker:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str], CircuitBreakerConfig] = {}
        self._states: dict[tuple[str, str], CircuitState] = {}

    def configure(self, installation_id: str, config: CircuitBreakerConfig) -> CircuitBreakerConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.failure_threshold < 1:
            raise ValueError("failure_threshold must be positive")
        key = (installation_id, config.endpoint_path)
        self._configs[key] = config
        if key not in self._states:
            self._states[key] = CircuitState(endpoint_path=config.endpoint_path)
        return config

    def get_state(self, installation_id: str, endpoint_path: str) -> CircuitState | None:
        return self._states.get((installation_id, endpoint_path))

    def is_allowed(self, installation_id: str, endpoint_path: str, now: datetime) -> bool:
        key = (installation_id, endpoint_path)
        state = self._states.get(key)
        if not state:
            return True  # no circuit breaker = allow
        config = self._configs.get(key, CircuitBreakerConfig(endpoint_path=endpoint_path))
        if state.state == "closed":
            return True
        if state.state == "open":
            if state.opened_at and now >= state.opened_at + timedelta(seconds=config.timeout_seconds):
                state.state = "half_open"
                state.success_count = 0
                return True
            return False
        # half_open: allow probe requests
        return True

    def record_success(self, installation_id: str, endpoint_path: str) -> CircuitState:
        key = (installation_id, endpoint_path)
        state = self._states.get(key)
        if not state:
            raise ValueError("No circuit breaker configured")
        config = self._configs.get(key, CircuitBreakerConfig(endpoint_path=endpoint_path))
        if state.state == "half_open":
            state.success_count += 1
            if state.success_count >= config.success_threshold:
                state.state = "closed"
                state.failure_count = 0
                log.info("circuit_closed", installation_id=installation_id, path=endpoint_path)
        elif state.state == "closed":
            state.failure_count = max(0, state.failure_count - 1)
        return state

    def record_failure(self, installation_id: str, endpoint_path: str, now: datetime) -> CircuitState:
        key = (installation_id, endpoint_path)
        state = self._states.get(key)
        if not state:
            raise ValueError("No circuit breaker configured")
        config = self._configs.get(key, CircuitBreakerConfig(endpoint_path=endpoint_path))
        state.failure_count += 1
        state.last_failure_at = now
        if state.state == "half_open":
            state.state = "open"
            state.opened_at = now
        elif state.state == "closed" and state.failure_count >= config.failure_threshold:
            state.state = "open"
            state.opened_at = now
            log.info("circuit_opened", installation_id=installation_id, path=endpoint_path)
        return state
