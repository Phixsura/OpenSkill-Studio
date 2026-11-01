"""Consumer API Webhook Delivery Report — generate periodic delivery reports."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryPeriod:
    period: str
    total_deliveries: int
    successful: int
    failed: int
    avg_latency_ms: float
    success_rate_pct: float

@dataclass
class DeliveryReport:
    consumer_id: str
    webhook_id: str
    periods: list[DeliveryPeriod] = field(default_factory=list)
    overall_success_rate: float = 100.0
    trend: str = "stable"

class AppAPIDeveloperPlatformSDKConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiConsumerApiApiConsumerWebhookDeliveryReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str, str], list[DeliveryPeriod]] = {}

    def add_period(self, installation_id: str, consumer_id: str, webhook_id: str, period: DeliveryPeriod) -> DeliveryPeriod:
        if not installation_id:
            raise ValueError("installation_id is required")
        if period.total_deliveries < 0:
            raise ValueError("total_deliveries must be non-negative")
        key = (installation_id, consumer_id, webhook_id)
        if key not in self._reports:
            self._reports[key] = []
        self._reports[key].append(period)
        self._reports[key].sort(key=lambda p: p.period)
        return period

    def generate_report(self, installation_id: str, consumer_id: str, webhook_id: str) -> DeliveryReport:
        periods = self._reports.get((installation_id, consumer_id, webhook_id), [])
        if not periods:
            return DeliveryReport(consumer_id=consumer_id, webhook_id=webhook_id)
        total_del = sum(p.total_deliveries for p in periods)
        total_ok = sum(p.successful for p in periods)
        overall_rate = round(total_ok / max(total_del, 1) * 100, 1)
        # Trend
        if len(periods) >= 2:
            recent = periods[-1].success_rate_pct
            prev = periods[-2].success_rate_pct
            if recent > prev + 5:
                trend = "improving"
            elif recent < prev - 5:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        return DeliveryReport(consumer_id=consumer_id, webhook_id=webhook_id, periods=periods, overall_success_rate=overall_rate, trend=trend)

    def list_webhooks(self, installation_id: str, consumer_id: str) -> list[str]:
        return sorted({wid for (inst, cid, wid) in self._reports if inst == installation_id and cid == consumer_id})
