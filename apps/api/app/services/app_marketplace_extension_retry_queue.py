"""Retry Queue — smart retry queue with exponential backoff and jitter.

Manages failed operations with configurable retry strategies, dead letter
handling, per-operation retry budgets, and backoff calculation.
"""
from __future__ import annotations
import math
import random
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class RetryStrategy(str, Enum):
    EXPONENTIAL = "exponential"
    LINEAR = "linear"
    FIXED = "fixed"


class ItemStatus(str, Enum):
    PENDING = "pending"
    RETRYING = "retrying"
    SUCCEEDED = "succeeded"
    DEAD_LETTER = "dead_letter"


@dataclass
class RetryItem:
    item_id: str
    operation: str
    payload: dict
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    status: ItemStatus = ItemStatus.PENDING
    attempt: int = 0
    max_attempts: int = 5
    base_delay_ms: int = 1000
    max_delay_ms: int = 60000
    next_retry_at: float = 0.0
    last_error: str = ""
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class RetryQueueService:
    """Manages retry queue with backoff strategies and dead letter."""

    def __init__(self):
        self._items: dict[str, RetryItem] = {}
        self._dead_letter: list[RetryItem] = []

    def enqueue(self, operation: str, payload: dict,
                strategy: RetryStrategy = RetryStrategy.EXPONENTIAL,
                max_attempts: int = 5,
                base_delay_ms: int = 1000) -> RetryItem:
        item_id = f"retry_{secrets.token_urlsafe(8)}"
        item = RetryItem(
            item_id=item_id, operation=operation, payload=payload,
            strategy=strategy, max_attempts=max_attempts,
            base_delay_ms=base_delay_ms,
        )
        self._items[item_id] = item
        return item

    def record_failure(self, item_id: str, error: str) -> RetryItem | None:
        item = self._items.get(item_id)
        if not item or item.status in (ItemStatus.SUCCEEDED, ItemStatus.DEAD_LETTER):
            return None

        item.attempt += 1
        item.last_error = error

        if item.attempt >= item.max_attempts:
            item.status = ItemStatus.DEAD_LETTER
            self._dead_letter.append(item)
        else:
            item.status = ItemStatus.RETRYING
            delay = self._calc_delay(item)
            item.next_retry_at = time.time() + delay / 1000

        return item

    def record_success(self, item_id: str) -> bool:
        item = self._items.get(item_id)
        if not item:
            return False
        item.status = ItemStatus.SUCCEEDED
        return True

    def _calc_delay(self, item: RetryItem) -> float:
        if item.strategy == RetryStrategy.FIXED:
            delay = item.base_delay_ms
        elif item.strategy == RetryStrategy.LINEAR:
            delay = item.base_delay_ms * item.attempt
        else:  # exponential
            delay = item.base_delay_ms * (2 ** (item.attempt - 1))

        # Add jitter (±25%)
        jitter = delay * 0.25 * (2 * random.random() - 1)
        delay = min(delay + jitter, item.max_delay_ms)
        return max(delay, 0)

    def get_ready(self, now: float | None = None) -> list[RetryItem]:
        current = now or time.time()
        return [item for item in self._items.values()
                if item.status == ItemStatus.RETRYING
                and item.next_retry_at <= current]

    def get_dead_letters(self) -> list[RetryItem]:
        return list(self._dead_letter)

    def retry_dead_letter(self, item_id: str, extra_attempts: int = 3) -> bool:
        item = self._items.get(item_id)
        if not item or item.status != ItemStatus.DEAD_LETTER:
            return False
        item.status = ItemStatus.RETRYING
        item.max_attempts += extra_attempts
        item.next_retry_at = time.time()
        self._dead_letter = [d for d in self._dead_letter if d.item_id != item_id]
        return True

    def get_stats(self) -> dict:
        items = list(self._items.values())
        return {
            "total": len(items),
            "pending": sum(1 for i in items if i.status == ItemStatus.PENDING),
            "retrying": sum(1 for i in items if i.status == ItemStatus.RETRYING),
            "succeeded": sum(1 for i in items if i.status == ItemStatus.SUCCEEDED),
            "dead_letter": len(self._dead_letter),
        }
