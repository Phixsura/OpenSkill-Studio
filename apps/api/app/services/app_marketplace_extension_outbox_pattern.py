"""Transactional Outbox — reliable event publishing with at-least-once delivery.

Implements:
- Outbox table pattern: events stored alongside business data
- Relay process polls and publishes pending events
- At-least-once delivery with idempotent consumers
- Dead letter after max publish attempts
- Ordered delivery per aggregate
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class OutboxEntry:
    entry_id: str
    aggregate_id: str
    event_type: str
    payload: dict
    status: str = "pending"  # pending, published, failed, dead
    attempts: int = 0
    max_attempts: int = 5
    created_at: float = 0.0
    published_at: float = 0.0
    last_attempt_at: float = 0.0
    error: str = ""
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class OutboxPatternService:
    def __init__(self):
        self._entries: list[OutboxEntry] = []
        self._counter = 0
        self._published_ids: set[str] = set()  # for consumer dedup

    def append(self, aggregate_id: str, event_type: str,
               payload: dict) -> OutboxEntry:
        """Called within the business transaction."""
        self._counter += 1
        entry = OutboxEntry(
            entry_id=f"outbox-{self._counter}",
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload)
        self._entries.append(entry)
        return entry

    def get_pending(self, batch_size: int = 10) -> list[OutboxEntry]:
        """Called by the relay process."""
        pending = [e for e in self._entries
                   if e.status == "pending"
                   and (e.last_attempt_at == 0 or
                        time.time() - e.last_attempt_at > 2 ** min(e.attempts, 6))]
        # Order by aggregate to maintain per-aggregate ordering
        pending.sort(key=lambda e: (e.aggregate_id, e.created_at))
        return pending[:batch_size]

    def mark_published(self, entry_id: str) -> bool:
        for e in self._entries:
            if e.entry_id == entry_id and e.status in ("pending", "failed"):
                e.status = "published"
                e.published_at = time.time()
                return True
        return False

    def mark_failed(self, entry_id: str, error: str = "") -> bool:
        for e in self._entries:
            if e.entry_id == entry_id:
                e.attempts += 1
                e.last_attempt_at = time.time()
                e.error = error
                if e.attempts >= e.max_attempts:
                    e.status = "dead"
                else:
                    e.status = "failed"
                return True
        return False

    def is_duplicate(self, entry_id: str) -> bool:
        """Consumer-side dedup check."""
        if entry_id in self._published_ids:
            return True
        self._published_ids.add(entry_id)
        return False

    def get_dead_letters(self) -> list[OutboxEntry]:
        return [e for e in self._entries if e.status == "dead"]

    def retry_dead(self, entry_id: str) -> bool:
        for e in self._entries:
            if e.entry_id == entry_id and e.status == "dead":
                e.status = "pending"
                e.attempts = 0
                e.error = ""
                return True
        return False

    def stats(self) -> dict:
        by_status = {}
        for e in self._entries:
            by_status[e.status] = by_status.get(e.status, 0) + 1
        return {
            "total": len(self._entries),
            "by_status": by_status,
            "oldest_pending_age": self._oldest_pending_age(),
        }

    def _oldest_pending_age(self) -> float:
        pending = [e for e in self._entries if e.status == "pending"]
        if not pending:
            return 0.0
        return round(time.time() - min(e.created_at for e in pending), 1)
