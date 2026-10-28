"""App Webhook Batch — batch multiple webhook events into single deliveries.

Manages webhook batching:
- Collect events within a time window
- Flush batches when full or on interval
- Track batch delivery stats
- Per-installation scoped batches
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class BatchedEvent:
    """An event in a batch."""

    event_id: str
    event_type: str
    payload: dict


@dataclass
class WebhookBatch:
    """A batch of webhook events."""

    batch_id: str
    destination: str
    events: list[BatchedEvent] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    flushed: bool = False
    delivered: bool = False


class AppWebhookBatch:
    """Batch multiple webhook events into single deliveries."""

    def __init__(self, max_batch_size: int = 100, flush_interval: float = 30.0) -> None:
        self._max_size = max(1, max_batch_size)
        self._flush_interval = flush_interval
        self._batches: dict[tuple[str, str], WebhookBatch] = {}
        self._completed: dict[str, list[WebhookBatch]] = {}

    def add_event(
        self, installation_id: str, destination: str,
        event_id: str, event_type: str, payload: dict,
    ) -> WebhookBatch:
        if not installation_id:
            raise ValueError("installation_id is required")

        key = (installation_id, destination)
        batch = self._batches.get(key)

        if batch is None or batch.flushed:
            batch_id = f"batch-{int(time.time() * 1000)}"
            batch = WebhookBatch(batch_id=batch_id, destination=destination)
            self._batches[key] = batch

        batch.events.append(BatchedEvent(
            event_id=event_id, event_type=event_type, payload=payload,
        ))

        # Auto-flush if max size reached
        if len(batch.events) >= self._max_size:
            self._flush(installation_id, batch)

        return batch

    def flush_ready(self, installation_id: str) -> list[WebhookBatch]:
        """Flush batches that have reached interval or max size."""
        now = time.time()
        ready = []
        for (inst, _), batch in self._batches.items():
            if inst != installation_id or batch.flushed:
                continue
            if (now - batch.created_at) >= self._flush_interval or len(batch.events) >= self._max_size:
                self._flush(installation_id, batch)
                ready.append(batch)
        return ready

    def mark_delivered(self, installation_id: str, batch_id: str) -> WebhookBatch:
        for batches in self._completed.get(installation_id, []):
            if batches.batch_id == batch_id:
                batches.delivered = True
                return batches
        raise KeyError(f"Batch {batch_id} not found")

    def pending_count(self, installation_id: str) -> int:
        return sum(
            len(b.events) for (inst, _), b in self._batches.items()
            if inst == installation_id and not b.flushed
        )

    def _flush(self, installation_id: str, batch: WebhookBatch) -> None:
        batch.flushed = True
        self._completed.setdefault(installation_id, []).append(batch)
