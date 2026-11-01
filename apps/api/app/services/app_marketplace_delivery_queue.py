"""Delivery Queue — ordered, persistent webhook delivery with deduplication.

Manages an ordered delivery queue with at-least-once semantics,
deduplication via idempotency keys, and delivery acknowledgment.
"""
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class DeliveryItem:
    delivery_id: str
    idempotency_key: str
    url: str
    payload: dict
    priority: int = 0
    created_at: str = ""
    attempts: int = 0
    acknowledged: bool = False
    last_error: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class DeliveryQueue:
    """Ordered delivery queue with deduplication and acknowledgment."""

    def __init__(self, max_size: int = 100000, max_attempts: int = 5):
        self._queue: deque[str] = deque()
        self._items: dict[str, DeliveryItem] = {}
        self._seen_keys: set[str] = set()
        self._max_size = max_size
        self._max_attempts = max_attempts
        self._dead_letter: list[DeliveryItem] = []

    def enqueue(self, item: DeliveryItem) -> tuple[bool, str]:
        """Add item to queue with deduplication."""
        if item.idempotency_key in self._seen_keys:
            return False, "Duplicate: idempotency key already seen"
        if len(self._queue) >= self._max_size:
            return False, "Queue is full"
        self._items[item.delivery_id] = item
        self._queue.append(item.delivery_id)
        self._seen_keys.add(item.idempotency_key)
        return True, "Enqueued"

    def dequeue(self, batch_size: int = 1) -> list[DeliveryItem]:
        """Dequeue items for delivery."""
        items = []
        while self._queue and len(items) < batch_size:
            delivery_id = self._queue.popleft()
            item = self._items.get(delivery_id)
            if item and not item.acknowledged:
                item.attempts += 1
                items.append(item)
        return items

    def acknowledge(self, delivery_id: str) -> bool:
        """Mark delivery as successfully completed."""
        item = self._items.get(delivery_id)
        if item:
            item.acknowledged = True
            return True
        return False

    def nack(self, delivery_id: str, error: str = "") -> bool:
        """Negative acknowledgment — requeue or dead letter."""
        item = self._items.get(delivery_id)
        if not item:
            return False
        item.last_error = error
        if item.attempts >= self._max_attempts:
            self._dead_letter.append(item)
            return True
        # Requeue at end
        self._queue.append(delivery_id)
        return True

    def peek(self, count: int = 5) -> list[DeliveryItem]:
        """Look at next items without dequeuing."""
        items = []
        for did in list(self._queue)[:count]:
            item = self._items.get(did)
            if item and not item.acknowledged:
                items.append(item)
        return items

    def get_dead_letter(self) -> list[DeliveryItem]:
        return list(self._dead_letter)

    def get_stats(self) -> dict:
        return {
            "queue_size": len(self._queue),
            "total_items": len(self._items),
            "acknowledged": sum(1 for i in self._items.values() if i.acknowledged),
            "dead_letter": len(self._dead_letter),
            "unique_keys": len(self._seen_keys),
        }
