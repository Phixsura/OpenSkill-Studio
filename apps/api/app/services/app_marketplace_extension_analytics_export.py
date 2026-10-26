"""Extension Analytics Export — generate downloadable analytics reports."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import json


@dataclass
class AnalyticsReport:
    report_id: str
    extension_id: str
    period: str  # daily, weekly, monthly
    metrics: dict = field(default_factory=dict)
    generated_at: float = 0.0
    def __post_init__(self):
        if not self.generated_at: self.generated_at = time.time()


class ExtAnalyticsExportService:
    def __init__(self):
        self._reports: dict[str, AnalyticsReport] = {}
        self._counter = 0
        self._raw_data: dict[str, list[dict]] = {}  # ext_id -> events

    def record_event(self, extension_id: str, event: str, value: float = 1.0) -> None:
        if extension_id not in self._raw_data:
            self._raw_data[extension_id] = []
        self._raw_data[extension_id].append({
            "event": event, "value": value, "ts": time.time()})

    def generate_report(self, extension_id: str, period: str = "daily") -> AnalyticsReport:
        self._counter += 1
        events = self._raw_data.get(extension_id, [])
        by_event: dict[str, float] = {}
        for e in events:
            by_event[e["event"]] = by_event.get(e["event"], 0) + e["value"]
        report = AnalyticsReport(
            report_id=f"rpt-{self._counter}", extension_id=extension_id,
            period=period, metrics={"total_events": len(events),
                                    "by_event": by_event, "period": period})
        self._reports[report.report_id] = report
        return report

    def export_json(self, report_id: str) -> str | None:
        r = self._reports.get(report_id)
        if not r: return None
        return json.dumps({"report_id": r.report_id, "extension_id": r.extension_id,
                           "period": r.period, "metrics": r.metrics}, indent=2)

    def list_reports(self, extension_id: str) -> list[AnalyticsReport]:
        return [r for r in self._reports.values() if r.extension_id == extension_id]
