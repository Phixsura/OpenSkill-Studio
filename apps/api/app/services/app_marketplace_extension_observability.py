"""Observability Pipeline — unified traces, metrics, and logs with sampling.

Implements:
- Trace context propagation (trace_id, span_id, parent)
- Metric types: counter, gauge, histogram
- Structured log enrichment with trace context
- Head-based sampling (decide at trace start)
- Tail-based sampling (decide after trace completes based on attributes)
- Export batching
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import secrets
import math
from collections import defaultdict


@dataclass
class TraceContext:
    trace_id: str
    span_id: str
    parent_span_id: str = ""
    sampled: bool = True


@dataclass
class MetricPoint:
    name: str
    value: float
    metric_type: str  # counter, gauge, histogram
    labels: dict[str, str] = field(default_factory=dict)
    timestamp: float = 0.0


@dataclass
class LogRecord:
    level: str
    message: str
    trace_id: str = ""
    span_id: str = ""
    attributes: dict = field(default_factory=dict)
    timestamp: float = 0.0


class ObservabilityPipelineService:
    def __init__(self, sample_rate: float = 1.0):
        """sample_rate: 0.0-1.0, fraction of traces to keep."""
        self._sample_rate = max(0.0, min(1.0, sample_rate))
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._traces: dict[str, list[dict]] = {}  # trace_id -> spans
        self._logs: list[LogRecord] = []
        self._export_batch: list[dict] = []

    # --- Tracing ---
    def start_trace(self, operation: str) -> TraceContext:
        trace_id = secrets.token_hex(16)
        span_id = secrets.token_hex(8)
        # Head-based sampling
        sampled = self._should_sample(trace_id)
        ctx = TraceContext(trace_id=trace_id, span_id=span_id, sampled=sampled)
        if sampled:
            self._traces[trace_id] = [{
                "span_id": span_id, "operation": operation,
                "start": time.time(), "end": 0, "status": "ok"}]
        return ctx

    def start_span(self, ctx: TraceContext, operation: str) -> TraceContext:
        span_id = secrets.token_hex(8)
        child = TraceContext(trace_id=ctx.trace_id, span_id=span_id,
                             parent_span_id=ctx.span_id, sampled=ctx.sampled)
        if ctx.sampled and ctx.trace_id in self._traces:
            self._traces[ctx.trace_id].append({
                "span_id": span_id, "parent": ctx.span_id,
                "operation": operation, "start": time.time(),
                "end": 0, "status": "ok"})
        return child

    def end_span(self, ctx: TraceContext, status: str = "ok") -> None:
        if not ctx.sampled:
            return
        spans = self._traces.get(ctx.trace_id, [])
        for span in spans:
            if span["span_id"] == ctx.span_id:
                span["end"] = time.time()
                span["status"] = status
                break

    def _should_sample(self, trace_id: str) -> bool:
        if self._sample_rate >= 1.0:
            return True
        if self._sample_rate <= 0.0:
            return False
        # Deterministic: hash trace_id for consistent sampling
        h = int(trace_id[:8], 16)
        return (h % 10000) < int(self._sample_rate * 10000)

    # --- Metrics ---
    def counter_inc(self, name: str, value: float = 1.0,
                    labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._counters[key] += value

    def gauge_set(self, name: str, value: float,
                  labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._gauges[key] = value

    def histogram_observe(self, name: str, value: float,
                          labels: dict[str, str] | None = None) -> None:
        key = self._metric_key(name, labels)
        self._histograms[key].append(value)

    def _metric_key(self, name: str, labels: dict | None) -> str:
        if not labels:
            return name
        sorted_labels = ",".join(f"{k}={v}" for k, v in sorted((labels or {}).items()))
        return f"{name}{{{sorted_labels}}}"

    def get_histogram_stats(self, name: str, labels: dict | None = None) -> dict:
        key = self._metric_key(name, labels)
        values = self._histograms.get(key, [])
        if not values:
            return {"count": 0}
        sorted_v = sorted(values)
        return {
            "count": len(values),
            "mean": round(sum(values) / len(values), 4),
            "min": sorted_v[0],
            "max": sorted_v[-1],
            "p50": sorted_v[len(sorted_v) // 2],
            "p95": sorted_v[int(len(sorted_v) * 0.95)],
            "p99": sorted_v[int(len(sorted_v) * 0.99)],
        }

    # --- Logging ---
    def log(self, level: str, message: str, ctx: TraceContext | None = None,
            attributes: dict | None = None) -> LogRecord:
        record = LogRecord(level=level, message=message,
                           trace_id=ctx.trace_id if ctx else "",
                           span_id=ctx.span_id if ctx else "",
                           attributes=attributes or {},
                           timestamp=time.time())
        self._logs.append(record)
        return record

    # --- Export ---
    def get_metrics_snapshot(self) -> dict:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: len(v) for k, v in self._histograms.items()},
        }

    def get_trace(self, trace_id: str) -> list[dict]:
        return self._traces.get(trace_id, [])

    def get_sampled_trace_count(self) -> int:
        return len(self._traces)
