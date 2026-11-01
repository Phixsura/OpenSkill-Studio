"""Consumer API Webhook Batch Sender — batch webhook delivery with aggregation."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class BatchEvent:
    event_id: str
    event_type: str
    payload: dict


@dataclass
class BatchConfig:
    max_batch_size: int = 50
    flush_interval_ms: int = 5000
    max_retries: int = 3


@dataclass
class BatchDelivery:
    batch_id: str
    webhook_url: str
    events: list[BatchEvent]
    status: str = "pending"  # pending, sent, failed
    attempt: int = 0
    response_code: int = 0


@dataclass
class WebhookBatchSender:
    """Aggregate events into batches for efficient webhook delivery."""

    _config: BatchConfig = field(default_factory=BatchConfig)
    _buffers: dict[str, list[BatchEvent]] = field(default_factory=dict)  # webhook_url -> events
    _deliveries: list[BatchDelivery] = field(default_factory=list)
    _batch_counter: int = 0

    def configure(self, max_batch_size: int = 50, flush_interval_ms: int = 5000,
                  max_retries: int = 3) -> dict:
        if max_batch_size < 1:
            raise ValueError("max_batch_size must be positive")
        self._config = BatchConfig(max_batch_size, flush_interval_ms, max_retries)
        return {"max_batch_size": max_batch_size, "flush_interval_ms": flush_interval_ms}

    def add_event(self, webhook_url: str, event: BatchEvent) -> dict:
        buffer = self._buffers.setdefault(webhook_url, [])
        buffer.append(event)
        auto_flush = len(buffer) >= self._config.max_batch_size
        result = {"buffered": True, "buffer_size": len(buffer), "auto_flush": auto_flush}
        if auto_flush:
            flush_result = self.flush(webhook_url)
            result["flush_result"] = flush_result
        return result

    def flush(self, webhook_url: str) -> dict:
        buffer = self._buffers.get(webhook_url, [])
        if not buffer:
            return {"flushed": 0}
        self._batch_counter += 1
        batch_id = f"batch-{self._batch_counter}"
        delivery = BatchDelivery(
            batch_id=batch_id, webhook_url=webhook_url,
            events=list(buffer), status="pending",
        )
        self._deliveries.append(delivery)
        self._buffers[webhook_url] = []
        logger.info("batch_flushed", batch_id=batch_id, events=len(delivery.events))
        return {"batch_id": batch_id, "flushed": len(delivery.events)}

    def flush_all(self) -> dict:
        total = 0
        batches = []
        for url in list(self._buffers.keys()):
            result = self.flush(url)
            if result["flushed"] > 0:
                total += result["flushed"]
                batches.append(result.get("batch_id"))
        return {"total_flushed": total, "batches": len(batches)}

    def mark_sent(self, batch_id: str, response_code: int = 200) -> dict:
        for d in self._deliveries:
            if d.batch_id == batch_id:
                d.status = "sent" if 200 <= response_code < 300 else "failed"
                d.response_code = response_code
                d.attempt += 1
                return {"batch_id": batch_id, "status": d.status}
        raise ValueError(f"Batch {batch_id} not found")

    def get_pending(self) -> list[dict]:
        return [
            {"batch_id": d.batch_id, "webhook_url": d.webhook_url,
             "event_count": len(d.events), "attempt": d.attempt}
            for d in self._deliveries if d.status == "pending"
        ]

    def get_buffer_status(self) -> dict:
        return {
            "buffers": {url: len(events) for url, events in self._buffers.items() if events},
            "total_buffered": sum(len(e) for e in self._buffers.values()),
        }

    def get_stats(self) -> dict:
        sent = sum(1 for d in self._deliveries if d.status == "sent")
        failed = sum(1 for d in self._deliveries if d.status == "failed")
        total_events = sum(len(d.events) for d in self._deliveries)
        return {
            "total_batches": len(self._deliveries),
            "sent": sent, "failed": failed,
            "pending": len(self._deliveries) - sent - failed,
            "total_events_delivered": total_events,
        }
