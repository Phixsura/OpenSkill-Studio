"""API Consumer Usage Report — generate periodic usage reports for consumers."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class UsageMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency_ms: float = 0.0
    unique_endpoints: int = 0
    data_transferred_bytes: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0: return 0.0
        return round((self.successful_requests / self.total_requests) * 100, 1)

    @property
    def avg_latency_ms(self) -> float:
        if self.total_requests == 0: return 0.0
        return round(self.total_latency_ms / self.total_requests, 2)

@dataclass
class UsageReport:
    report_id: str
    consumer_id: str
    period: str  # "daily", "weekly", "monthly"
    metrics: UsageMetrics
    top_endpoints: list[dict[str, object]] = field(default_factory=list)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerUsageReport:
    def __init__(self) -> None:
        self._reports: dict[tuple[str, str], list[UsageReport]] = {}
        self._metrics: dict[tuple[str, str], UsageMetrics] = {}

    def record(self, installation_id: str, consumer_id: str, endpoint: str, latency_ms: float, success: bool, bytes_transferred: int = 0) -> None:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        m = self._metrics.get(key)
        if m is None: m = UsageMetrics(); self._metrics[key] = m
        m.total_requests += 1
        m.total_latency_ms += latency_ms
        m.data_transferred_bytes += bytes_transferred
        if success: m.successful_requests += 1
        else: m.failed_requests += 1

    def generate_report(self, installation_id: str, consumer_id: str, report_id: str, period: str = "daily") -> UsageReport:
        key = (installation_id, consumer_id)
        m = self._metrics.get(key)
        if m is None: m = UsageMetrics()
        report = UsageReport(report_id=report_id, consumer_id=consumer_id, period=period, metrics=m)
        self._reports.setdefault(key, []).append(report)
        return report

    def get_metrics(self, installation_id: str, consumer_id: str) -> UsageMetrics:
        return self._metrics.get((installation_id, consumer_id), UsageMetrics())

    def list_reports(self, installation_id: str, consumer_id: str | None = None) -> list[UsageReport]:
        if consumer_id:
            return self._reports.get((installation_id, consumer_id), [])
        return [r for (inst, _), reports in self._reports.items() if inst == installation_id for r in reports]

    def consumer_count(self, installation_id: str) -> int:
        return len({cid for (inst, cid) in self._metrics if inst == installation_id})
