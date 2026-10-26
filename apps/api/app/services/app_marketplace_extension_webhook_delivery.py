"""Webhook Delivery Queue — reliable webhook delivery with exponential backoff.

Manages a delivery queue with configurable retry policies, circuit breaker
pattern, dead letter queue, and delivery metrics per endpoint.
"""
from __future__ import annotations
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class DeliveryState(str, Enum):
    QUEUED = "queued"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class WebhookDelivery:
    delivery_id: str
    endpoint_id: str
    url: str
    payload: str
    state: DeliveryState = DeliveryState.QUEUED
    attempts: int = 0
    max_retries: int = 5
    last_status_code: int = 0
    last_error: str = ""
    next_retry_at: float = 0
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


@dataclass
class EndpointHealth:
    endpoint_id: str
    url: str
    circuit_state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    total_deliveries: int = 0
    total_failures: int = 0
    failure_threshold: int = 5


class WebhookDeliveryService:
    """Manages webhook delivery with retry, circuit breaker, and dead letter."""

    BACKOFF_BASE = 2.0
    MAX_BACKOFF = 3600

    def __init__(self):
        self._queue: list[WebhookDelivery] = []
        self._endpoints: dict[str, EndpointHealth] = {}
        self._dead_letter: list[WebhookDelivery] = []

    def register_endpoint(self, endpoint_id: str, url: str,
                          failure_threshold: int = 5) -> EndpointHealth:
        health = EndpointHealth(
            endpoint_id=endpoint_id, url=url,
            failure_threshold=failure_threshold,
        )
        self._endpoints[endpoint_id] = health
        return health

    def enqueue(self, endpoint_id: str, payload: str,
                max_retries: int = 5) -> WebhookDelivery | None:
        ep = self._endpoints.get(endpoint_id)
        if not ep:
            return None
        if ep.circuit_state == CircuitState.OPEN:
            return None  # circuit breaker open

        delivery = WebhookDelivery(
            delivery_id=f"dlv_{secrets.token_urlsafe(10)}",
            endpoint_id=endpoint_id, url=ep.url,
            payload=payload, max_retries=max_retries,
        )
        self._queue.append(delivery)
        return delivery

    def process_result(self, delivery_id: str, success: bool,
                       status_code: int = 0, error: str = "") -> WebhookDelivery | None:
        delivery = next((d for d in self._queue if d.delivery_id == delivery_id), None)
        if not delivery:
            return None

        delivery.attempts += 1
        delivery.last_status_code = status_code
        ep = self._endpoints.get(delivery.endpoint_id)

        if success:
            delivery.state = DeliveryState.DELIVERED
            if ep:
                ep.total_deliveries += 1
                ep.consecutive_failures = 0
                if ep.circuit_state == CircuitState.HALF_OPEN:
                    ep.circuit_state = CircuitState.CLOSED
        else:
            delivery.last_error = error
            if ep:
                ep.total_failures += 1
                ep.consecutive_failures += 1
                if ep.consecutive_failures >= ep.failure_threshold:
                    ep.circuit_state = CircuitState.OPEN

            if delivery.attempts >= delivery.max_retries:
                delivery.state = DeliveryState.DEAD_LETTER
                self._dead_letter.append(delivery)
            else:
                delivery.state = DeliveryState.RETRYING
                backoff = min(self.BACKOFF_BASE ** delivery.attempts, self.MAX_BACKOFF)
                import time
                delivery.next_retry_at = time.time() + backoff

        return delivery

    def reset_circuit(self, endpoint_id: str) -> bool:
        ep = self._endpoints.get(endpoint_id)
        if ep and ep.circuit_state == CircuitState.OPEN:
            ep.circuit_state = CircuitState.HALF_OPEN
            ep.consecutive_failures = 0
            return True
        return False

    def get_queue_stats(self) -> dict:
        by_state: dict[str, int] = defaultdict(int)
        for d in self._queue:
            by_state[d.state.value] += 1
        return {"total": len(self._queue), "dead_letter": len(self._dead_letter),
                "by_state": dict(by_state)}

    def get_dead_letters(self, endpoint_id: str | None = None) -> list[WebhookDelivery]:
        if endpoint_id:
            return [d for d in self._dead_letter if d.endpoint_id == endpoint_id]
        return list(self._dead_letter)
