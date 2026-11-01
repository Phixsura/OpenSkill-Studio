"""App API Developer Webhook Delivery Report — periodic webhook delivery summary reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryReport:
    report_id: str
    period: str
    total_deliveries: int
    successful: int
    failed: int
    avg_latency_ms: float
    destinations_count: int

    @property
    def success_rate(self) -> float:
        return round(self.successful / self.total_deliveries * 100, 1) if self.total_deliveries > 0 else 100.0

    @property
    def health_status(self) -> str:
        r = self.success_rate
        if r >= 99: return "excellent"
        if r >= 95: return "good"
        if r >= 90: return "fair"
        return "poor"

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperApiApiApiDeveloperApiApiWebhookDeliveryReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], DeliveryReport] = {}

    def generate(self, installation_id: str, report_id: str, period: str, total: int, successful: int, failed: int, avg_latency_ms: float, destinations_count: int) -> DeliveryReport:
        if not installation_id: raise ValueError("installation_id is required")
        r = DeliveryReport(report_id=report_id, period=period, total_deliveries=total, successful=successful, failed=failed, avg_latency_ms=avg_latency_ms, destinations_count=destinations_count)
        self._reports[(installation_id, report_id)] = r
        return r

    def get(self, installation_id: str, report_id: str) -> DeliveryReport | None:
        return self._reports.get((installation_id, report_id))

    def trend(self, installation_id: str) -> list[DeliveryReport]:
        reports = [r for (inst, _), r in self._reports.items() if inst == installation_id]
        return sorted(reports, key=lambda r: r.period)

    def worst_period(self, installation_id: str) -> DeliveryReport | None:
        reports = self.trend(installation_id)
        return min(reports, key=lambda r: r.success_rate) if reports else None
