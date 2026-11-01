"""Consumer Webhook Retry Queue — dead letter queue with manual retry."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class FailedDelivery:
    delivery_id: str
    webhook_id: str
    event_type: str
    payload: dict
    error: str
    attempts: int = 1
    max_attempts: int = 5
    status: str = "pending"  # pending, retrying, succeeded, dead
    failed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_retry_at: str = ""


@dataclass
class RetryQueue:
    """Dead letter queue for failed webhook deliveries with manual retry."""

    _queue: dict[str, FailedDelivery] = field(default_factory=dict)

    def enqueue(self, delivery: FailedDelivery) -> dict:
        if delivery.delivery_id in self._queue:
            existing = self._queue[delivery.delivery_id]
            existing.attempts += 1
            existing.error = delivery.error
            if existing.attempts >= existing.max_attempts:
                existing.status = "dead"
            return {"delivery_id": delivery.delivery_id, "attempts": existing.attempts,
                    "status": existing.status}
        self._queue[delivery.delivery_id] = delivery
        logger.info("delivery_enqueued", delivery_id=delivery.delivery_id)
        return {"delivery_id": delivery.delivery_id, "attempts": 1, "status": "pending"}

    def retry(self, delivery_id: str, success: bool = False) -> dict:
        item = self._queue.get(delivery_id)
        if not item:
            raise ValueError(f"Delivery {delivery_id} not found")
        if item.status == "dead":
            raise ValueError("Cannot retry dead delivery — use resurrect")
        if success:
            item.status = "succeeded"
            return {"delivery_id": delivery_id, "status": "succeeded"}
        item.attempts += 1
        item.last_retry_at = datetime.now(timezone.utc).isoformat()
        if item.attempts >= item.max_attempts:
            item.status = "dead"
        else:
            item.status = "retrying"
        logger.info("delivery_retried", delivery_id=delivery_id, attempts=item.attempts)
        return {"delivery_id": delivery_id, "attempts": item.attempts, "status": item.status}

    def resurrect(self, delivery_id: str) -> dict:
        item = self._queue.get(delivery_id)
        if not item:
            raise ValueError(f"Delivery {delivery_id} not found")
        if item.status != "dead":
            return {"resurrected": False, "reason": "not_dead"}
        item.status = "pending"
        item.attempts = 0
        logger.info("delivery_resurrected", delivery_id=delivery_id)
        return {"resurrected": True, "delivery_id": delivery_id}

    def get_pending(self, limit: int = 50) -> list[dict]:
        items = [d for d in self._queue.values() if d.status in ("pending", "retrying")]
        items.sort(key=lambda x: x.failed_at)
        return [self._to_dict(d) for d in items[:limit]]

    def get_dead_letters(self, limit: int = 50) -> list[dict]:
        items = [d for d in self._queue.values() if d.status == "dead"]
        return [self._to_dict(d) for d in items[:limit]]

    def purge_succeeded(self) -> dict:
        before = len(self._queue)
        self._queue = {k: v for k, v in self._queue.items() if v.status != "succeeded"}
        return {"purged": before - len(self._queue)}

    def _to_dict(self, d: FailedDelivery) -> dict:
        return {
            "delivery_id": d.delivery_id, "webhook_id": d.webhook_id,
            "event_type": d.event_type, "error": d.error,
            "attempts": d.attempts, "max_attempts": d.max_attempts,
            "status": d.status, "failed_at": d.failed_at,
        }

    def get_stats(self) -> dict:
        items = list(self._queue.values())
        return {
            "total": len(items),
            "pending": sum(1 for d in items if d.status == "pending"),
            "retrying": sum(1 for d in items if d.status == "retrying"),
            "dead": sum(1 for d in items if d.status == "dead"),
            "succeeded": sum(1 for d in items if d.status == "succeeded"),
        }
