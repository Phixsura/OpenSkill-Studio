"""Consumer API Webhook Batch Sender — batch multiple events into single webhook deliveries."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import structlog

log = structlog.get_logger()

@dataclass
class BatchConfig:
    consumer_id: str
    webhook_id: str
    max_batch_size: int = 50
    max_wait_seconds: int = 10
    enabled: bool = True

@dataclass
class PendingEvent:
    event_id: str
    event_type: str
    payload: dict
    received_at: datetime

@dataclass
class BatchDelivery:
    batch_id: str
    webhook_id: str
    events: list[PendingEvent]
    created_at: datetime
    payload_size_bytes: int

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiWebhookBatchSender:
    def __init__(self) -> None:
        self._configs: dict[tuple[str, str, str], BatchConfig] = {}
        self._pending: dict[tuple[str, str, str], list[PendingEvent]] = {}
        self._deliveries: list[BatchDelivery] = []

    def configure(self, installation_id: str, config: BatchConfig) -> BatchConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if config.max_batch_size < 1:
            raise ValueError("max_batch_size must be positive")
        if config.max_wait_seconds < 1:
            raise ValueError("max_wait_seconds must be positive")
        self._configs[(installation_id, config.consumer_id, config.webhook_id)] = config
        return config

    def add_event(self, installation_id: str, consumer_id: str, webhook_id: str, event: PendingEvent) -> int:
        key = (installation_id, consumer_id, webhook_id)
        if key not in self._pending:
            self._pending[key] = []
        self._pending[key].append(event)
        return len(self._pending[key])

    def should_flush(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> bool:
        key = (installation_id, consumer_id, webhook_id)
        config = self._configs.get(key, BatchConfig(consumer_id=consumer_id, webhook_id=webhook_id))
        pending = self._pending.get(key, [])
        if not pending:
            return False
        if len(pending) >= config.max_batch_size:
            return True
        oldest = pending[0].received_at
        if (now - oldest).total_seconds() >= config.max_wait_seconds:
            return True
        return False

    def flush(self, installation_id: str, consumer_id: str, webhook_id: str, now: datetime) -> BatchDelivery | None:
        key = (installation_id, consumer_id, webhook_id)
        pending = self._pending.get(key, [])
        if not pending:
            return None
        payload = json.dumps([{"event_id": e.event_id, "event_type": e.event_type, "payload": e.payload} for e in pending])
        delivery = BatchDelivery(batch_id=f"batch-{now.isoformat()}", webhook_id=webhook_id, events=list(pending), created_at=now, payload_size_bytes=len(payload.encode()))
        self._deliveries.append(delivery)
        self._pending[key] = []
        log.info("batch_flushed", installation_id=installation_id, consumer=consumer_id, events=len(delivery.events))
        return delivery

    def get_pending_count(self, installation_id: str, consumer_id: str, webhook_id: str) -> int:
        return len(self._pending.get((installation_id, consumer_id, webhook_id), []))
