"""App API Error Report — generate periodic error reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ErrorSummary:
    error_code: str
    count: int
    first_seen: str = ""
    last_seen: str = ""

@dataclass
class ErrorReport:
    report_id: str
    period: str
    errors: list[ErrorSummary] = field(default_factory=list)
    total_errors: int = 0
    total_requests: int = 0

    @property
    def error_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.total_errors / self.total_requests * 100, 2)

class AppAPIErrorReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], ErrorReport] = {}

    def generate(self, installation_id: str, report_id: str, period: str, errors: list[dict], total_requests: int) -> ErrorReport:
        if not installation_id: raise ValueError("installation_id is required")
        summaries = [ErrorSummary(error_code=e["code"], count=e["count"]) for e in errors]
        total_errors = sum(s.count for s in summaries)
        report = ErrorReport(report_id=report_id, period=period, errors=summaries, total_errors=total_errors, total_requests=total_requests)
        self._reports[(installation_id, report_id)] = report
        return report

    def get_report(self, installation_id: str, report_id: str) -> ErrorReport:
        r = self._reports.get((installation_id, report_id))
        if r is None: raise KeyError(f"Report {report_id} not found")
        return r

    def list_reports(self, installation_id: str) -> list[ErrorReport]:
        return [r for (inst, _), r in self._reports.items() if inst == installation_id]
