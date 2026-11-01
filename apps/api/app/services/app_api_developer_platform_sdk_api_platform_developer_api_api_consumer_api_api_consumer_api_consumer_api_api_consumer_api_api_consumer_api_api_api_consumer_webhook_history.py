"""Consumer API Webhook History — complete webhook delivery history."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class WebhookDeliveryRecord:
    delivery_id: str
    webhook_id: str
    consumer_id: str
    event_type: str
    url: str
    status_code: int | None = None
    latency_ms: float = 0.0
    success: bool = False
    attempt: int = 1
    error: str | None = None
    timestamp: datetime | None = None
    payload_size_bytes: int = 0

@dataclass
class WebhookHistorySummary:
    total_deliveries: int
    successful: int
    failed: int
    avg_latency_ms: float
    success_rate_pct: float

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiApiConsumerApiApiApiConsumerWebhookHistory:
    def __init__(self, max_per_consumer: int = 10000) -> None:
        self._records: dict[tuple[str, str], list[WebhookDeliveryRecord]] = {}
        self._max = max_per_consumer

    def record(self, installation_id: str, delivery: WebhookDeliveryRecord) -> WebhookDeliveryRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        delivery.timestamp = delivery.timestamp or datetime.utcnow()
        key = (installation_id, delivery.consumer_id)
        if key not in self._records:
            self._records[key] = []
        self._records[key].append(delivery)
        if len(self._records[key]) > self._max:
            self._records[key] = self._records[key][-self._max:]
        return delivery

    def query(self, installation_id: str, consumer_id: str, webhook_id: str | None = None, event_type: str | None = None, success: bool | None = None, limit: int = 50) -> list[WebhookDeliveryRecord]:
        records = self._records.get((installation_id, consumer_id), [])
        if webhook_id:
            records = [r for r in records if r.webhook_id == webhook_id]
        if event_type:
            records = [r for r in records if r.event_type == event_type]
        if success is not None:
            records = [r for r in records if r.success == success]
        return list(reversed(records[-limit:]))

    def get_summary(self, installation_id: str, consumer_id: str) -> WebhookHistorySummary:
        records = self._records.get((installation_id, consumer_id), [])
        if not records:
            return WebhookHistorySummary(total_deliveries=0, successful=0, failed=0, avg_latency_ms=0, success_rate_pct=100)
        ok = sum(1 for r in records if r.success)
        successful_latencies = [r.latency_ms for r in records if r.success and r.latency_ms > 0]
        avg_lat = sum(successful_latencies) / len(successful_latencies) if successful_latencies else 0
        return WebhookHistorySummary(total_deliveries=len(records), successful=ok, failed=len(records) - ok, avg_latency_ms=round(avg_lat, 1), success_rate_pct=round(ok / len(records) * 100, 1))
