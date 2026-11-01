"""Consumer API Webhook Circuit Breaker — protect webhook endpoints from cascading failures."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class WebhookCircuitConfig:
    webhook_id: str
    consumer_id: str
    failure_threshold: int = 5
    success_threshold: int = 3
    timeout_seconds: int = 60

@dataclass
class CircuitState:
    webhook_id: str
    state: str = "closed"  # "closed", "open", "half_open"
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    opened_at: datetime | None = None
    total_failures: int = 0
    total_successes: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookCircuitBreaker:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], WebhookCircuitConfig] = {}
        self._states: dict[tuple[str, str, str], CircuitState] = {}

    def configure(self, installation_id: str, config: WebhookCircuitConfig) -> WebhookCircuitConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, config.consumer_id, config.webhook_id)
        self._configs[key] = config
        if key not in self._states:
            self._states[key] = CircuitState(webhook_id=config.webhook_id)
        return config

    def should_deliver(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> bool:
        key = (installation_id, consumer_id, webhook_id)
        state = self._states.get(key)
        if not state:
            return True
        config = self._configs.get(key, WebhookCircuitConfig(webhook_id=webhook_id, consumer_id=consumer_id))
        if state.state == "closed":
            return True
        if state.state == "open":
            if state.opened_at and now >= state.opened_at + timedelta(seconds=config.timeout_seconds):
                state.state = "half_open"
                state.consecutive_successes = 0
                return True
            return False
        return True  # half_open: allow probe

    def record_success(self, installation_id: str, consumer_id: str, webhook_id: str) -> CircuitState:
        key = (installation_id, consumer_id, webhook_id)
        state = self._states.get(key)
        if not state:
            state = CircuitState(webhook_id=webhook_id)
            self._states[key] = state
        config = self._configs.get(key, WebhookCircuitConfig(webhook_id=webhook_id, consumer_id=consumer_id))
        state.total_successes += 1
        state.consecutive_failures = 0
        state.consecutive_successes += 1
        if state.state == "half_open" and state.consecutive_successes >= config.success_threshold:
            state.state = "closed"
            log.info("webhook_circuit_closed", webhook_id=webhook_id)
        return state

    def record_failure(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> CircuitState:
        key = (installation_id, consumer_id, webhook_id)
        state = self._states.get(key)
        if not state:
            state = CircuitState(webhook_id=webhook_id)
            self._states[key] = state
        config = self._configs.get(key, WebhookCircuitConfig(webhook_id=webhook_id, consumer_id=consumer_id))
        state.total_failures += 1
        state.consecutive_failures += 1
        state.consecutive_successes = 0
        if state.state == "half_open":
            state.state = "open"
            state.opened_at = now
        elif state.state == "closed" and state.consecutive_failures >= config.failure_threshold:
            state.state = "open"
            state.opened_at = now
            log.info("webhook_circuit_opened", webhook_id=webhook_id)
        return state

    def get_state(self, installation_id: str, consumer_id: str, webhook_id: str) -> CircuitState | None:
        return self._states.get((installation_id, consumer_id, webhook_id))
