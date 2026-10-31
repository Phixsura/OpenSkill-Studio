"""Consumer API Request Debugger — request debugging with trace replay."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class TraceSpan:
    span_id: str
    name: str
    start_ms: float
    duration_ms: float
    status: str = "ok"  # ok, error
    metadata: dict = field(default_factory=dict)
    children: list[TraceSpan] = field(default_factory=list)


@dataclass
class DebugTrace:
    trace_id: str
    request_id: str
    method: str
    url: str
    status_code: int
    total_duration_ms: float
    spans: list[TraceSpan] = field(default_factory=list)
    error: str = ""


@dataclass
class RequestDebugger:
    """Debug API requests with distributed trace analysis."""

    _traces: dict[str, DebugTrace] = field(default_factory=dict)

    def record_trace(self, trace: DebugTrace) -> dict:
        self._traces[trace.trace_id] = trace
        logger.info("trace_recorded", trace_id=trace.trace_id)
        return {"trace_id": trace.trace_id, "spans": len(trace.spans)}

    def get_trace(self, trace_id: str) -> dict | None:
        trace = self._traces.get(trace_id)
        if not trace:
            return None
        return {
            "trace_id": trace.trace_id,
            "request_id": trace.request_id,
            "method": trace.method,
            "url": trace.url,
            "status_code": trace.status_code,
            "total_duration_ms": trace.total_duration_ms,
            "span_count": len(trace.spans),
            "error": trace.error or None,
            "spans": [self._span_to_dict(s) for s in trace.spans],
        }

    def _span_to_dict(self, span: TraceSpan) -> dict:
        return {
            "span_id": span.span_id,
            "name": span.name,
            "start_ms": span.start_ms,
            "duration_ms": span.duration_ms,
            "status": span.status,
            "children": [self._span_to_dict(c) for c in span.children],
        }

    def find_bottleneck(self, trace_id: str) -> dict | None:
        trace = self._traces.get(trace_id)
        if not trace or not trace.spans:
            return None
        slowest = max(trace.spans, key=lambda s: s.duration_ms)
        return {
            "trace_id": trace_id,
            "bottleneck_span": slowest.span_id,
            "name": slowest.name,
            "duration_ms": slowest.duration_ms,
            "pct_of_total": round(slowest.duration_ms / trace.total_duration_ms * 100, 1)
            if trace.total_duration_ms > 0 else 0,
        }

    def find_errors(self, trace_id: str) -> list[dict]:
        trace = self._traces.get(trace_id)
        if not trace:
            return []
        errors = []
        def collect(spans: list[TraceSpan]) -> None:
            for s in spans:
                if s.status == "error":
                    errors.append({"span_id": s.span_id, "name": s.name,
                                   "duration_ms": s.duration_ms})
                collect(s.children)
        collect(trace.spans)
        return errors

    def list_traces(self, method: str | None = None, error_only: bool = False,
                    limit: int = 20) -> list[dict]:
        traces = list(self._traces.values())
        if method:
            traces = [t for t in traces if t.method == method.upper()]
        if error_only:
            traces = [t for t in traces if t.error or t.status_code >= 400]
        return [
            {"trace_id": t.trace_id, "method": t.method, "url": t.url,
             "status_code": t.status_code, "duration_ms": t.total_duration_ms,
             "has_error": bool(t.error)}
            for t in list(reversed(traces))[:limit]
        ]

    def get_stats(self) -> dict:
        traces = list(self._traces.values())
        errors = sum(1 for t in traces if t.error or t.status_code >= 400)
        durations = [t.total_duration_ms for t in traces] if traces else [0]
        return {
            "total_traces": len(traces),
            "error_traces": errors,
            "avg_duration_ms": round(sum(durations) / len(durations), 2),
            "max_duration_ms": max(durations),
        }
