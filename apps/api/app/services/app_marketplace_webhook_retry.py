"""Webhook Retry — exponential backoff retry for failed webhook deliveries.

Manages retry queues with configurable backoff, max attempts,
dead letter queue, and delivery status tracking.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    RETRYING = "retrying"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class WebhookDelivery:
    delivery_id: str
    subscription_id: str
    url: str
    event_type: str
    payload: dict
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempt: int = 0
    max_attempts: int = 5
    next_retry_at: str = ""
    last_error: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class WebhookRetryManager:
    """Manages webhook delivery retries with exponential backoff."""

    def __init__(self, base_delay_seconds: float = 10.0, max_delay_seconds: float = 3600.0):
        self._deliveries: dict[str, WebhookDelivery] = {}
        self._dead_letter: list[WebhookDelivery] = []
        self._base_delay = base_delay_seconds
        self._max_delay = max_delay_seconds

    def create_delivery(self, delivery_id: str, sub_id: str, url: str,
                        event_type: str, payload: dict, max_attempts: int = 5) -> WebhookDelivery:
        delivery = WebhookDelivery(
            delivery_id=delivery_id, subscription_id=sub_id, url=url,
            event_type=event_type, payload=payload, max_attempts=max_attempts,
        )
        self._deliveries[delivery_id] = delivery
        return delivery

    def calculate_backoff(self, attempt: int) -> float:
        """Calculate exponential backoff with jitter cap."""
        delay = self._base_delay * (2 ** attempt)
        return min(delay, self._max_delay)

    def record_success(self, delivery_id: str) -> bool:
        d = self._deliveries.get(delivery_id)
        if d:
            d.status = DeliveryStatus.DELIVERED
            d.attempt += 1
            return True
        return False

    def record_failure(self, delivery_id: str, error: str) -> DeliveryStatus:
        """Record a delivery failure and schedule retry or dead-letter."""
        d = self._deliveries.get(delivery_id)
        if not d:
            return DeliveryStatus.FAILED
        d.attempt += 1
        d.last_error = error

        if d.attempt >= d.max_attempts:
            d.status = DeliveryStatus.DEAD_LETTER
            self._dead_letter.append(d)
            return DeliveryStatus.DEAD_LETTER

        d.status = DeliveryStatus.RETRYING
        backoff = self.calculate_backoff(d.attempt)
        d.next_retry_at = f"+{backoff}s"
        return DeliveryStatus.RETRYING

    def get_retryable(self) -> list[WebhookDelivery]:
        return [d for d in self._deliveries.values() if d.status == DeliveryStatus.RETRYING]

    def get_dead_letter_queue(self) -> list[WebhookDelivery]:
        return list(self._dead_letter)

    def get_delivery(self, delivery_id: str) -> WebhookDelivery | None:
        return self._deliveries.get(delivery_id)

    def get_stats(self) -> dict:
        all_d = list(self._deliveries.values())
        return {
            "total": len(all_d),
            "delivered": sum(1 for d in all_d if d.status == DeliveryStatus.DELIVERED),
            "retrying": sum(1 for d in all_d if d.status == DeliveryStatus.RETRYING),
            "dead_letter": len(self._dead_letter),
            "pending": sum(1 for d in all_d if d.status == DeliveryStatus.PENDING),
        }
