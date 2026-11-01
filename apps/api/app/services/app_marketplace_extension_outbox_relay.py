"""Outbox Relay — reliable message delivery from outbox to message broker.

The relay component that polls the outbox table and publishes to
the message broker, handling failures and ordering.

Implements:
- Poll-based relay with configurable batch size
- Ordered delivery per partition key
- Deduplication on the consumer side
- Delivery confirmation with offset tracking
- Poison message detection (stuck messages)
- Relay metrics (throughput, latency, failures)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from collections import defaultdict


@dataclass
class OutboxMessage:
    message_id: str
    partition_key: str
    topic: str
    payload: dict
    created_at: float
    attempts: int = 0
    max_attempts: int = 5
    last_attempt_at: float = 0.0
    delivered: bool = False
    poison: bool = False


class OutboxRelayService:
    BACKOFF_BASE = 1.0  # seconds

    def __init__(self):
        self._outbox: list[OutboxMessage] = []
        self._delivered_ids: set[str] = set()
        self._consumer_dedup: set[str] = set()
        self._metrics = {
            "total_polled": 0, "total_delivered": 0,
            "total_failed": 0, "total_poison": 0,
        }
        self._partition_offsets: dict[str, int] = defaultdict(int)

    def enqueue(self, message_id: str, partition_key: str, topic: str,
                payload: dict) -> OutboxMessage:
        msg = OutboxMessage(message_id=message_id, partition_key=partition_key,
                            topic=topic, payload=payload,
                            created_at=time.time())
        self._outbox.append(msg)
        return msg

    def poll(self, batch_size: int = 10) -> list[OutboxMessage]:
        """Poll for undelivered messages respecting backoff."""
        now = time.time()
        eligible = []
        for msg in self._outbox:
            if msg.delivered or msg.poison:
                continue
            if msg.last_attempt_at > 0:
                backoff = self.BACKOFF_BASE * (2 ** min(msg.attempts, 6))
                if now - msg.last_attempt_at < backoff:
                    continue
            eligible.append(msg)

        # Sort by partition key then created_at for ordering
        eligible.sort(key=lambda m: (m.partition_key, m.created_at))
        batch = eligible[:batch_size]
        self._metrics["total_polled"] += len(batch)
        return batch

    def deliver(self, message_id: str, publisher: callable | None = None) -> dict:
        """Attempt to deliver a message."""
        msg = next((m for m in self._outbox if m.message_id == message_id), None)
        if not msg:
            return {"status": "not_found"}
        if msg.delivered:
            return {"status": "already_delivered"}

        msg.attempts += 1
        msg.last_attempt_at = time.time()

        success = True
        if publisher:
            try:
                publisher(msg.topic, msg.partition_key, msg.payload)
            except Exception as e:
                success = False
                if msg.attempts >= msg.max_attempts:
                    msg.poison = True
                    self._metrics["total_poison"] += 1
                    return {"status": "poison", "error": str(e),
                            "attempts": msg.attempts}
                self._metrics["total_failed"] += 1
                return {"status": "failed", "error": str(e),
                        "retry_attempt": msg.attempts}

        msg.delivered = True
        self._delivered_ids.add(message_id)
        self._metrics["total_delivered"] += 1
        self._partition_offsets[msg.partition_key] = max(
            self._partition_offsets[msg.partition_key],
            int(msg.created_at * 1000))
        return {"status": "delivered"}

    def relay_batch(self, batch_size: int = 10,
                    publisher: callable | None = None) -> dict:
        """Poll + deliver a batch. Returns summary."""
        batch = self.poll(batch_size)
        results = {"delivered": 0, "failed": 0, "poison": 0}
        for msg in batch:
            result = self.deliver(msg.message_id, publisher)
            if result["status"] == "delivered":
                results["delivered"] += 1
            elif result["status"] == "poison":
                results["poison"] += 1
            else:
                results["failed"] += 1
        return results

    def is_duplicate(self, message_id: str) -> bool:
        """Consumer-side dedup check."""
        if message_id in self._consumer_dedup:
            return True
        self._consumer_dedup.add(message_id)
        return False

    def get_poison_messages(self) -> list[OutboxMessage]:
        return [m for m in self._outbox if m.poison]

    def retry_poison(self, message_id: str) -> bool:
        msg = next((m for m in self._outbox if m.message_id == message_id), None)
        if msg and msg.poison:
            msg.poison = False
            msg.attempts = 0
            return True
        return False

    def get_metrics(self) -> dict:
        pending = sum(1 for m in self._outbox if not m.delivered and not m.poison)
        return {**self._metrics, "pending": pending,
                "outbox_size": len(self._outbox)}
