"""App Webhook Queue — queue and deliver webhooks with ordering.

Manages webhook delivery queue:
- Enqueue webhooks with ordering guarantees
- Process in FIFO order per destination
- Track delivery attempts and status
- Dead letter queue for failed deliveries
- Per-installation scoped queues
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class DeliveryStatus(str, Enum):
    QUEUED = "queued"
    DELIVERING = "delivering"
    DELIVERED = "delivered"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class QueuedWebhook:
    """A queued webhook."""

    webhook_id: str
    destination: str
    payload: str
    status: DeliveryStatus = DeliveryStatus.QUEUED
    attempts: int = 0
    max_attempts: int = 5
    created_at: float = field(default_factory=time.time)
    error: str = ""


class AppWebhookQueue:
    """Queue and deliver webhooks with ordering."""

    def __init__(self) -> None:
        self._queues: dict[str, list[QueuedWebhook]] = {}

    def enqueue(
        self, installation_id: str, webhook_id: str, destination: str,
        payload: str, max_attempts: int = 5,
    ) -> QueuedWebhook:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not destination:
            raise ValueError("destination is required")

        wh = QueuedWebhook(
            webhook_id=webhook_id, destination=destination,
            payload=payload, max_attempts=max_attempts,
        )
        self._queues.setdefault(installation_id, []).append(wh)
        return wh

    def next(self, installation_id: str) -> QueuedWebhook | None:
        """Get next queued webhook (FIFO)."""
        for wh in self._queues.get(installation_id, []):
            if wh.status == DeliveryStatus.QUEUED:
                wh.status = DeliveryStatus.DELIVERING
                wh.attempts += 1
                return wh
        return None

    def mark_delivered(self, installation_id: str, webhook_id: str) -> QueuedWebhook:
        wh = self._find(installation_id, webhook_id)
        wh.status = DeliveryStatus.DELIVERED
        return wh

    def mark_failed(self, installation_id: str, webhook_id: str, error: str = "") -> QueuedWebhook:
        wh = self._find(installation_id, webhook_id)
        wh.error = error
        if wh.attempts >= wh.max_attempts:
            wh.status = DeliveryStatus.DEAD_LETTER
        else:
            wh.status = DeliveryStatus.QUEUED  # re-queue for retry
        return wh

    def dead_letters(self, installation_id: str) -> list[QueuedWebhook]:
        return [
            wh for wh in self._queues.get(installation_id, [])
            if wh.status == DeliveryStatus.DEAD_LETTER
        ]

    def queue_depth(self, installation_id: str) -> int:
        return sum(
            1 for wh in self._queues.get(installation_id, [])
            if wh.status == DeliveryStatus.QUEUED
        )

    def stats(self, installation_id: str) -> dict[str, int]:
        webhooks = self._queues.get(installation_id, [])
        return {s.value: sum(1 for w in webhooks if w.status == s) for s in DeliveryStatus}

    def _find(self, installation_id: str, webhook_id: str) -> QueuedWebhook:
        for wh in self._queues.get(installation_id, []):
            if wh.webhook_id == webhook_id:
                return wh
        raise KeyError(f"Webhook {webhook_id} not found")
