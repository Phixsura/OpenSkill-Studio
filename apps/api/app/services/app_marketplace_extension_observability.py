"""Observability — distributed tracing and span management for extensions.

Creates trace contexts with parent/child spans, timing, annotations,
error tracking, and trace export for debugging extension execution.
"""
from __future__ import annotations
import secrets
import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class Span:
    span_id: str
    trace_id: str
    name: str
    parent_id: str = ""
    start_time: float = 0.0
    end_time: float = 0.0
    duration_ms: float = 0.0
    status: str = "ok"  # ok, error
    attributes: dict = field(default_factory=dict)
    events: list[dict] = field(default_factory=list)


class ObservabilityService:
    """Manages distributed traces with hierarchical spans."""

    def __init__(self):
        self._traces: dict[str, list[Span]] = defaultdict(list)

    def start_trace(self, name: str, attributes: dict | None = None) -> Span:
        trace_id = f"tr_{secrets.token_urlsafe(12)}"
        span_id = f"sp_{secrets.token_urlsafe(8)}"
        span = Span(
            span_id=span_id, trace_id=trace_id, name=name,
            start_time=time.time(), attributes=attributes or {},
        )
        self._traces[trace_id].append(span)
        return span

    def start_span(self, trace_id: str, name: str,
                   parent_id: str = "", attributes: dict | None = None) -> Span:
        span_id = f"sp_{secrets.token_urlsafe(8)}"
        span = Span(
            span_id=span_id, trace_id=trace_id, name=name,
            parent_id=parent_id, start_time=time.time(),
            attributes=attributes or {},
        )
        self._traces[trace_id].append(span)
        return span

    def end_span(self, trace_id: str, span_id: str,
                 status: str = "ok", attributes: dict | None = None) -> bool:
        spans = self._traces.get(trace_id, [])
        span = next((s for s in spans if s.span_id == span_id), None)
        if not span:
            return False
        span.end_time = time.time()
        span.duration_ms = round((span.end_time - span.start_time) * 1000, 2)
        span.status = status
        if attributes:
            span.attributes.update(attributes)
        return True

    def add_event(self, trace_id: str, span_id: str,
                  name: str, attributes: dict | None = None) -> bool:
        spans = self._traces.get(trace_id, [])
        span = next((s for s in spans if s.span_id == span_id), None)
        if not span:
            return False
        span.events.append({
            "name": name, "timestamp": time.time(),
            "attributes": attributes or {},
        })
        return True

    def get_trace(self, trace_id: str) -> list[Span]:
        return self._traces.get(trace_id, [])

    def get_trace_tree(self, trace_id: str) -> dict:
        spans = self._traces.get(trace_id, [])
        if not spans:
            return {}
        root = next((s for s in spans if not s.parent_id), spans[0])
        return self._build_tree(root, spans)

    def _build_tree(self, node: Span, all_spans: list[Span]) -> dict:
        children = [s for s in all_spans if s.parent_id == node.span_id]
        return {
            "span_id": node.span_id, "name": node.name,
            "duration_ms": node.duration_ms, "status": node.status,
            "children": [self._build_tree(c, all_spans) for c in children],
        }

    def get_slow_spans(self, trace_id: str, threshold_ms: float = 100) -> list[Span]:
        return [s for s in self._traces.get(trace_id, [])
                if s.duration_ms > threshold_ms]

    def get_error_spans(self, trace_id: str) -> list[Span]:
        return [s for s in self._traces.get(trace_id, [])
                if s.status == "error"]
