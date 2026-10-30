"""Consumer API Usage Report — generate periodic usage reports per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import structlog

log = structlog.get_logger()

@dataclass
class UsageMetric:
    metric: str
    value: float
    unit: str = ""
    change_pct: float = 0.0  # vs previous period

@dataclass
class UsageReport:
    report_id: str
    consumer_id: str
    period: str  # "2026-06", "2026-Q2", "2026-W22"
    generated_at: datetime
    metrics: list[UsageMetric] = field(default_factory=list)
    total_cost_cents: int = 0
    status: str = "generated"  # "generated", "delivered", "acknowledged"

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiUsageReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], UsageReport] = {}

    def generate(self, installation_id: str, report: UsageReport) -> UsageReport:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not report.metrics:
            raise ValueError("Report must include at least one metric")
        key = (installation_id, report.report_id)
        if key in self._reports:
            raise ValueError(f"Report {report.report_id} already exists")
        self._reports[key] = report
        log.info("usage_report_generated", installation_id=installation_id, consumer=report.consumer_id, period=report.period)
        return report

    def mark_delivered(self, installation_id: str, report_id: str) -> UsageReport:
        key = (installation_id, report_id)
        report = self._reports.get(key)
        if not report:
            raise ValueError("Report not found")
        report.status = "delivered"
        return report

    def acknowledge(self, installation_id: str, report_id: str) -> UsageReport:
        key = (installation_id, report_id)
        report = self._reports.get(key)
        if not report:
            raise ValueError("Report not found")
        report.status = "acknowledged"
        return report

    def get_report(self, installation_id: str, report_id: str) -> UsageReport | None:
        return self._reports.get((installation_id, report_id))

    def list_reports(self, installation_id: str, consumer_id: str) -> list[UsageReport]:
        return sorted([r for (inst, _), r in self._reports.items() if inst == installation_id and r.consumer_id == consumer_id], key=lambda r: r.period, reverse=True)

    def total_cost(self, installation_id: str, consumer_id: str) -> int:
        return sum(r.total_cost_cents for (inst, _), r in self._reports.items() if inst == installation_id and r.consumer_id == consumer_id)
