"""Consumer API Usage Report — periodic usage reports with export."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class UsageEntry:
    endpoint_id: str
    period: str
    requests: int
    errors: int = 0
    avg_latency_ms: float = 0.0
    bandwidth_bytes: int = 0


@dataclass
class UsageReport:
    report_id: str
    consumer_id: str
    period_start: str
    period_end: str
    entries: list[UsageEntry] = field(default_factory=list)
    generated_at: str = ""
    status: str = "draft"  # draft, finalized, exported


@dataclass
class UsageReportGenerator:
    """Generate periodic usage reports with aggregation and export."""

    _reports: dict[str, UsageReport] = field(default_factory=dict)
    _raw_data: dict[str, list[UsageEntry]] = field(default_factory=dict)  # consumer -> entries

    def record(self, consumer_id: str, entry: UsageEntry) -> dict:
        self._raw_data.setdefault(consumer_id, []).append(entry)
        return {"consumer_id": consumer_id,
                "total_entries": len(self._raw_data[consumer_id])}

    def generate(self, report_id: str, consumer_id: str,
                 period_start: str, period_end: str) -> dict:
        if report_id in self._reports:
            raise ValueError(f"Report {report_id} already exists")
        entries = self._raw_data.get(consumer_id, [])
        period_entries = [e for e in entries
                          if period_start <= e.period <= period_end]
        # Aggregate by endpoint
        agg: dict[str, dict] = {}
        for e in period_entries:
            if e.endpoint_id not in agg:
                agg[e.endpoint_id] = {"requests": 0, "errors": 0,
                                       "latencies": [], "bandwidth": 0}
            a = agg[e.endpoint_id]
            a["requests"] += e.requests
            a["errors"] += e.errors
            a["latencies"].append(e.avg_latency_ms)
            a["bandwidth"] += e.bandwidth_bytes
        aggregated = []
        for eid, a in agg.items():
            avg_lat = sum(a["latencies"]) / len(a["latencies"]) if a["latencies"] else 0
            aggregated.append(UsageEntry(
                endpoint_id=eid, period=f"{period_start}~{period_end}",
                requests=a["requests"], errors=a["errors"],
                avg_latency_ms=round(avg_lat, 2), bandwidth_bytes=a["bandwidth"],
            ))
        report = UsageReport(
            report_id=report_id, consumer_id=consumer_id,
            period_start=period_start, period_end=period_end,
            entries=aggregated,
        )
        self._reports[report_id] = report
        logger.info("report_generated", report_id=report_id)
        return {"report_id": report_id, "endpoints": len(aggregated),
                "total_requests": sum(e.requests for e in aggregated)}

    def finalize(self, report_id: str) -> dict:
        report = self._reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        report.status = "finalized"
        return {"report_id": report_id, "status": "finalized"}

    def export_csv(self, report_id: str) -> str:
        report = self._reports.get(report_id)
        if not report:
            raise ValueError(f"Report {report_id} not found")
        lines = ["endpoint_id,requests,errors,avg_latency_ms,bandwidth_bytes"]
        for e in report.entries:
            lines.append(f"{e.endpoint_id},{e.requests},{e.errors},{e.avg_latency_ms},{e.bandwidth_bytes}")
        report.status = "exported"
        return "\n".join(lines)

    def get_report(self, report_id: str) -> dict | None:
        report = self._reports.get(report_id)
        if not report:
            return None
        total_reqs = sum(e.requests for e in report.entries)
        total_errors = sum(e.errors for e in report.entries)
        return {
            "report_id": report.report_id,
            "consumer_id": report.consumer_id,
            "period": f"{report.period_start} to {report.period_end}",
            "status": report.status,
            "endpoints": len(report.entries),
            "total_requests": total_reqs,
            "total_errors": total_errors,
            "error_rate": round(total_errors / total_reqs * 100, 2) if total_reqs > 0 else 0,
        }

    def list_reports(self, consumer_id: str | None = None) -> list[dict]:
        reports = list(self._reports.values())
        if consumer_id:
            reports = [r for r in reports if r.consumer_id == consumer_id]
        return [self.get_report(r.report_id) for r in reports]
