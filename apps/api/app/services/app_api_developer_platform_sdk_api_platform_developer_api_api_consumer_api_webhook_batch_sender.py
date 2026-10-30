"""API Consumer Webhook Batch Sender — send webhooks in batches for efficiency."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class BatchEvent:
    event_id: str
    event_type: str
    payload_size_bytes: int = 0

@dataclass
class WebhookBatch:
    batch_id: str
    consumer_id: str
    events: list[BatchEvent] = field(default_factory=list)
    sent_at: float = 0.0
    success: bool | None = None
    response_status: int = 0

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiWebhookBatchSender:
    def __init__(self, max_batch_size: int = 100, max_payload_bytes: int = 1048576) -> None:
        self._batches: dict[str, list[WebhookBatch]] = {}
        self._max_size = max(1, max_batch_size)
        self._max_bytes = max(1024, max_payload_bytes)

    def create_batch(self, installation_id: str, batch_id: str, consumer_id: str, events: list[BatchEvent]) -> WebhookBatch:
        if not installation_id: raise ValueError("installation_id is required")
        if not events: raise ValueError("Batch must contain events")
        if len(events) > self._max_size: raise ValueError(f"Batch too large: {len(events)} > {self._max_size}")
        total_bytes = sum(e.payload_size_bytes for e in events)
        if total_bytes > self._max_bytes: raise ValueError(f"Payload too large: {total_bytes} > {self._max_bytes}")
        batch = WebhookBatch(batch_id=batch_id, consumer_id=consumer_id, events=events)
        self._batches.setdefault(installation_id, []).append(batch)
        return batch

    def mark_sent(self, installation_id: str, batch_id: str, response_status: int) -> WebhookBatch:
        for b in self._batches.get(installation_id, []):
            if b.batch_id == batch_id:
                b.sent_at = time.time()
                b.response_status = response_status
                b.success = 200 <= response_status < 300
                return b
        raise KeyError(f"Batch {batch_id} not found")

    def pending_batches(self, installation_id: str) -> list[WebhookBatch]:
        return [b for b in self._batches.get(installation_id, []) if b.success is None]

    def stats(self, installation_id: str) -> dict[str, int]:
        batches = self._batches.get(installation_id, [])
        return {"total": len(batches), "pending": sum(1 for b in batches if b.success is None), "success": sum(1 for b in batches if b.success is True), "failed": sum(1 for b in batches if b.success is False), "total_events": sum(len(b.events) for b in batches)}
