"""App Telemetry Collector — structured telemetry ingestion from installed apps.

Collects runtime telemetry from sandboxed app executions:
- Custom metric recording (counters, gauges, histograms)
- Error reporting with stack traces
- Performance spans with duration
- Telemetry quotas per installation
- Aggregation by time window
- Top errors ranking
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()


class MetricKind(str, Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"


@dataclass
class TelemetryMetric:
    """A single metric data point."""
    name: str
    kind: MetricKind
    value: float
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ErrorReport:
    """An error reported by an app."""
    error_type: str
    message: str
    stack_trace: str | None = None
    context: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class PerformanceSpan:
    """A timed operation span."""
    operation: str
    duration_ms: float
    status: str = "ok"
    tags: dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class TelemetrySummary:
    """Aggregated telemetry for an installation."""
    installation_id: str
    total_metrics: int
    total_errors: int
    total_spans: int
    error_rate: float
    avg_span_ms: float
    top_errors: list[tuple[str, int]]
    top_slow_ops: list[tuple[str, float]]


TELEMETRY_QUOTA_PER_HOUR = 10_000


class AppTelemetryCollector:
    """Collect and query app telemetry."""

    def __init__(self):
        self._metrics: dict[str, list[TelemetryMetric]] = defaultdict(list)
        self._errors: dict[str, list[ErrorReport]] = defaultdict(list)
        self._spans: dict[str, list[PerformanceSpan]] = defaultdict(list)
        self._hourly_counts: dict[tuple[str, str], int] = defaultdict(int)

    def _check_quota(self, installation_id: str) -> bool:
        hk = datetime.now(UTC).strftime("%Y-%m-%dT%H")
        count = self._hourly_counts[(installation_id, hk)]
        return count < TELEMETRY_QUOTA_PER_HOUR

    def _increment_quota(self, installation_id: str) -> None:
        hk = datetime.now(UTC).strftime("%Y-%m-%dT%H")
        self._hourly_counts[(installation_id, hk)] += 1

    # ── Ingestion ────────────────────────────────────────

    def record_metric(self, installation_id: str, metric: TelemetryMetric) -> bool:
        if not self._check_quota(installation_id):
            return False
        self._metrics[installation_id].append(metric)
        self._increment_quota(installation_id)
        return True

    def report_error(self, installation_id: str, error: ErrorReport) -> bool:
        if not self._check_quota(installation_id):
            return False
        self._errors[installation_id].append(error)
        self._increment_quota(installation_id)
        return True

    def record_span(self, installation_id: str, span: PerformanceSpan) -> bool:
        if not self._check_quota(installation_id):
            return False
        self._spans[installation_id].append(span)
        self._increment_quota(installation_id)
        return True

    # ── Queries ──────────────────────────────────────────

    def get_metrics(self, installation_id: str, name: str | None = None,
                    limit: int = 100) -> list[TelemetryMetric]:
        metrics = self._metrics.get(installation_id, [])
        if name:
            metrics = [m for m in metrics if m.name == name]
        return metrics[-limit:]

    def get_errors(self, installation_id: str, limit: int = 50) -> list[ErrorReport]:
        return self._errors.get(installation_id, [])[-limit:]

    def get_spans(self, installation_id: str, operation: str | None = None,
                  limit: int = 100) -> list[PerformanceSpan]:
        spans = self._spans.get(installation_id, [])
        if operation:
            spans = [s for s in spans if s.operation == operation]
        return spans[-limit:]

    def get_summary(self, installation_id: str) -> TelemetrySummary:
        metrics = self._metrics.get(installation_id, [])
        errors = self._errors.get(installation_id, [])
        spans = self._spans.get(installation_id, [])

        total = len(metrics) + len(errors) + len(spans)
        error_rate = (len(errors) / total * 100) if total > 0 else 0.0

        avg_span = 0.0
        if spans:
            avg_span = sum(s.duration_ms for s in spans) / len(spans)

        error_counts = Counter(e.error_type for e in errors)
        top_errors = error_counts.most_common(5)

        span_avgs: dict[str, list[float]] = defaultdict(list)
        for s in spans:
            span_avgs[s.operation].append(s.duration_ms)
        top_slow = sorted(
            [(op, sum(ds) / len(ds)) for op, ds in span_avgs.items()],
            key=lambda x: x[1], reverse=True,
        )[:5]

        return TelemetrySummary(
            installation_id=installation_id,
            total_metrics=len(metrics),
            total_errors=len(errors),
            total_spans=len(spans),
            error_rate=round(error_rate, 2),
            avg_span_ms=round(avg_span, 2),
            top_errors=top_errors,
            top_slow_ops=top_slow,
        )

    def get_quota_usage(self, installation_id: str) -> int:
        hk = datetime.now(UTC).strftime("%Y-%m-%dT%H")
        return self._hourly_counts.get((installation_id, hk), 0)
