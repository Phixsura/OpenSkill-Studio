"""App API Developer API Request Trace Collector — distributed tracing for API calls."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TraceSpan:
    span_id: str
    trace_id: str
    operation: str
    service: str
    duration_ms: float
    status: str = "ok"  # "ok", "error"
    parent_span_id: str | None = None
    timestamp: float = field(default_factory=time.time)

@dataclass
class Trace:
    trace_id: str
    spans: list[TraceSpan] = field(default_factory=list)

    @property
    def total_duration_ms(self) -> float:
        if not self.spans: return 0.0
        return round(max(s.timestamp + s.duration_ms / 1000 for s in self.spans) - min(s.timestamp for s in self.spans), 1) * 1000

    @property
    def has_errors(self) -> bool:
        return any(s.status == "error" for s in self.spans)

class AppAPIDeveloperAPIApiRequestTraceCollector:
    def __init__(self, max_traces: int = 1000) -> None:
        self._max = max(1, max_traces)
        self._traces: dict[tuple[str, str], Trace] = {}

    def record_span(self, installation_id: str, trace_id: str, span_id: str, operation: str, service: str, duration_ms: float, status: str = "ok", parent_span_id: str | None = None) -> Trace:
        if not installation_id: raise ValueError("installation_id is required")
        if status not in ("ok", "error"): raise ValueError("invalid status")
        key = (installation_id, trace_id)
        if key not in self._traces:
            self._traces[key] = Trace(trace_id=trace_id)
        t = self._traces[key]
        t.spans.append(TraceSpan(span_id=span_id, trace_id=trace_id, operation=operation, service=service, duration_ms=duration_ms, status=status, parent_span_id=parent_span_id))
        return t

    def get_trace(self, installation_id: str, trace_id: str) -> Trace:
        key = (installation_id, trace_id)
        t = self._traces.get(key)
        if t is None: raise KeyError(f"Trace {trace_id} not found")
        return t

    def error_traces(self, installation_id: str) -> list[Trace]:
        return [t for (inst, _), t in self._traces.items() if inst == installation_id and t.has_errors]

    def slow_traces(self, installation_id: str, threshold_ms: float = 1000) -> list[Trace]:
        return [t for (inst, _), t in self._traces.items() if inst == installation_id and t.total_duration_ms > threshold_ms]

    def trace_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._traces if inst == installation_id)
