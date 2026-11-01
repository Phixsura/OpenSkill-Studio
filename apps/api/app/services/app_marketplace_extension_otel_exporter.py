"""Extension OpenTelemetry Exporter — traces and spans for extension observability."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import secrets


@dataclass
class Span:
    trace_id: str
    span_id: str
    name: str
    extension_id: str
    parent_span_id: str = ""
    status: str = "ok"  # ok, error, unset
    start_time: float = 0.0
    end_time: float = 0.0
    attributes: dict = field(default_factory=dict)
    def __post_init__(self):
        if not self.start_time: self.start_time = time.time()

    @property
    def duration_ms(self) -> float:
        if self.end_time <= 0: return 0
        return round((self.end_time - self.start_time) * 1000, 2)


class ExtOtelExporterService:
    def __init__(self):
        self._traces: dict[str, list[Span]] = {}  # trace_id -> spans

    def start_trace(self, extension_id: str, name: str,
                    attributes: dict | None = None) -> Span:
        trace_id = secrets.token_hex(16)
        span_id = secrets.token_hex(8)
        span = Span(trace_id=trace_id, span_id=span_id, name=name,
                     extension_id=extension_id, attributes=attributes or {})
        self._traces[trace_id] = [span]
        return span

    def start_span(self, trace_id: str, name: str, parent_span_id: str,
                   extension_id: str, attributes: dict | None = None) -> Span | None:
        if trace_id not in self._traces:
            return None
        span_id = secrets.token_hex(8)
        span = Span(trace_id=trace_id, span_id=span_id, name=name,
                     extension_id=extension_id, parent_span_id=parent_span_id,
                     attributes=attributes or {})
        self._traces[trace_id].append(span)
        return span

    def end_span(self, trace_id: str, span_id: str, status: str = "ok") -> bool:
        spans = self._traces.get(trace_id, [])
        for s in spans:
            if s.span_id == span_id:
                s.end_time = time.time()
                s.status = status
                return True
        return False

    def get_trace(self, trace_id: str) -> list[Span]:
        return self._traces.get(trace_id, [])

    def get_slow_traces(self, threshold_ms: float = 1000) -> list[tuple[str, float]]:
        slow = []
        for tid, spans in self._traces.items():
            root = spans[0] if spans else None
            if root and root.duration_ms > threshold_ms:
                slow.append((tid, root.duration_ms))
        return sorted(slow, key=lambda x: x[1], reverse=True)
