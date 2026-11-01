"""App API Developer API Uptime Report — periodic uptime summary reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UptimeReport:
    report_id: str
    period: str
    uptime_pct: float
    total_checks: int
    downtime_minutes: float
    incidents: int

class AppAPIDeveloperAPIUptimeReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], UptimeReport] = {}

    def generate(self, installation_id: str, report_id: str, period: str, uptime_pct: float, total_checks: int, downtime_minutes: float, incidents: int) -> UptimeReport:
        if not installation_id: raise ValueError("installation_id is required")
        r = UptimeReport(report_id=report_id, period=period, uptime_pct=uptime_pct, total_checks=total_checks, downtime_minutes=downtime_minutes, incidents=incidents)
        self._reports[(installation_id, report_id)] = r
        return r

    def list_reports(self, installation_id: str) -> list[UptimeReport]:
        return [r for (inst, _), r in self._reports.items() if inst == installation_id]

    def best_period(self, installation_id: str) -> UptimeReport | None:
        reports = self.list_reports(installation_id)
        return max(reports, key=lambda r: r.uptime_pct) if reports else None
