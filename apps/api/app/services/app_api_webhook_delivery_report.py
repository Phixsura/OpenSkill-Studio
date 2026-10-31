"""App API Webhook Delivery Report — periodic delivery summary reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class DeliveryReport:
    report_id: str
    period: str
    total_sent: int
    total_failed: int
    success_rate: float
    avg_latency_ms: float
    top_destination: str = ""
    top_event_type: str = ""

class AppAPIWebhookDeliveryReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], DeliveryReport] = {}

    def generate(self, installation_id: str, report_id: str, period: str, total_sent: int, total_failed: int, avg_latency_ms: float, top_destination: str = "", top_event_type: str = "") -> DeliveryReport:
        if not installation_id: raise ValueError("installation_id is required")
        total = total_sent + total_failed
        rate = round(total_sent / total * 100, 1) if total > 0 else 100.0
        r = DeliveryReport(report_id=report_id, period=period, total_sent=total_sent, total_failed=total_failed, success_rate=rate, avg_latency_ms=avg_latency_ms, top_destination=top_destination, top_event_type=top_event_type)
        self._reports[(installation_id, report_id)] = r
        return r

    def get(self, installation_id: str, report_id: str) -> DeliveryReport:
        r = self._reports.get((installation_id, report_id))
        if r is None: raise KeyError(f"Report {report_id} not found")
        return r

    def list_reports(self, installation_id: str) -> list[DeliveryReport]:
        return [r for (inst, _), r in self._reports.items() if inst == installation_id]
