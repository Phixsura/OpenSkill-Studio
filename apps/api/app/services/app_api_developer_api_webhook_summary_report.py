"""App API Developer Webhook Summary Report — periodic webhook summary."""
from __future__ import annotations
from dataclasses import dataclass
import structlog

log = structlog.get_logger()

@dataclass
class WebhookSummaryReport:
    report_id: str
    period: str
    total_events: int
    total_deliveries: int
    success_rate: float
    avg_latency_ms: float
    top_event: str = ""
    top_destination: str = ""

class AppAPIDeveloperAPIWebhookSummaryReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], WebhookSummaryReport] = {}

    def generate(self, installation_id: str, report_id: str, period: str, total_events: int, total_deliveries: int, success_rate: float, avg_latency_ms: float, top_event: str = "", top_destination: str = "") -> WebhookSummaryReport:
        if not installation_id: raise ValueError("installation_id is required")
        r = WebhookSummaryReport(report_id=report_id, period=period, total_events=total_events, total_deliveries=total_deliveries, success_rate=success_rate, avg_latency_ms=avg_latency_ms, top_event=top_event, top_destination=top_destination)
        self._reports[(installation_id, report_id)] = r
        return r

    def list_reports(self, installation_id: str) -> list[WebhookSummaryReport]:
        return [r for (inst, _), r in self._reports.items() if inst == installation_id]
