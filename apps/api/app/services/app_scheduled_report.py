"""App Scheduled Report — generate and deliver periodic reports.

Manages scheduled report generation:
- Define reports with schedule and recipients
- Track generation history
- Enable/disable reports
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ScheduledReport:
    """A scheduled report definition."""

    report_id: str
    name: str
    schedule: str  # "daily", "weekly", "monthly"
    format: str  # "pdf", "csv", "html"
    recipients: list[str]
    enabled: bool = True
    last_generated_at: float | None = None
    generation_count: int = 0


class AppScheduledReport:
    """Generate and deliver periodic reports."""

    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], ScheduledReport] = {}

    def create_report(
        self,
        installation_id: str,
        report_id: str,
        name: str,
        schedule: str,
        fmt: str,
        recipients: list[str],
    ) -> ScheduledReport:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not report_id:
            raise ValueError("report_id is required")
        if schedule not in ("daily", "weekly", "monthly"):
            raise ValueError("schedule must be daily, weekly, or monthly")
        if not recipients:
            raise ValueError("at least one recipient required")

        key = (installation_id, report_id)
        if key in self._reports:
            raise ValueError(f"Report {report_id} already exists")

        report = ScheduledReport(
            report_id=report_id, name=name, schedule=schedule,
            format=fmt, recipients=recipients,
        )
        self._reports[key] = report
        return report

    def record_generation(
        self, installation_id: str, report_id: str, now: float | None = None
    ) -> ScheduledReport:
        r = self._get(installation_id, report_id)
        r.last_generated_at = now or time.time()
        r.generation_count += 1
        return r

    def enable(self, installation_id: str, report_id: str) -> ScheduledReport:
        r = self._get(installation_id, report_id)
        r.enabled = True
        return r

    def disable(self, installation_id: str, report_id: str) -> ScheduledReport:
        r = self._get(installation_id, report_id)
        r.enabled = False
        return r

    def list_reports(self, installation_id: str, enabled_only: bool = False) -> list[ScheduledReport]:
        reports = [r for (inst, _), r in self._reports.items() if inst == installation_id]
        if enabled_only:
            reports = [r for r in reports if r.enabled]
        return reports

    def _get(self, installation_id: str, report_id: str) -> ScheduledReport:
        key = (installation_id, report_id)
        r = self._reports.get(key)
        if r is None:
            raise KeyError(f"Report {report_id} not found")
        return r
