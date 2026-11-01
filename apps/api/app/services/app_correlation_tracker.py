"""App Correlation Tracker — trace request correlation across services.

Tracks request correlation IDs for distributed tracing:
- Generate and propagate correlation IDs
- Link parent-child spans
- Track timing and status per span
- Per-installation scoped traces
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Span:
    """A single span in a trace."""

    span_id: str
    trace_id: str
    installation_id: str
    service: str
    operation: str
    parent_span_id: str | None = None
    started_at: float = field(default_factory=time.time)
    ended_at: float | None = None
    status: str = "ok"  # "ok", "error"
    duration_ms: float | None = None
    metadata: dict = field(default_factory=dict)


class AppCorrelationTracker:
    """Trace request correlation across services."""

    def __init__(self) -> None:
        # (installation_id, span_id) → Span
        self._spans: dict[tuple[str, str], Span] = {}
        # trace_id → list of span_ids
        self._traces: dict[str, list[str]] = {}

    def generate_trace_id(self) -> str:
        return secrets.token_hex(16)

    def start_span(
        self,
        installation_id: str,
        span_id: str,
        trace_id: str,
        service: str,
        operation: str,
        parent_span_id: str | None = None,
        now: float | None = None,
    ) -> Span:
        """Start a new span."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not span_id:
            raise ValueError("span_id is required")
        if not service:
            raise ValueError("service is required")

        key = (installation_id, span_id)
        if key in self._spans:
            raise ValueError(f"Span {span_id} already exists")

        span = Span(
            span_id=span_id,
            trace_id=trace_id,
            installation_id=installation_id,
            service=service,
            operation=operation,
            parent_span_id=parent_span_id,
            started_at=now or time.time(),
        )
        self._spans[key] = span
        self._traces.setdefault(trace_id, []).append(span_id)
        return span

    def end_span(
        self,
        installation_id: str,
        span_id: str,
        status: str = "ok",
        now: float | None = None,
    ) -> Span:
        """End a span."""
        span = self._get(installation_id, span_id)
        if span.ended_at is not None:
            raise ValueError("Span already ended")
        now = now or time.time()
        span.ended_at = now
        span.status = status
        span.duration_ms = (now - span.started_at) * 1000
        return span

    def get_trace(self, installation_id: str, trace_id: str) -> list[Span]:
        """Get all spans in a trace, ordered by start time."""
        span_ids = self._traces.get(trace_id, [])
        spans = []
        for sid in span_ids:
            key = (installation_id, sid)
            span = self._spans.get(key)
            if span:
                spans.append(span)
        return sorted(spans, key=lambda s: s.started_at)

    def get_span(self, installation_id: str, span_id: str) -> Span:
        return self._get(installation_id, span_id)

    def get_children(self, installation_id: str, span_id: str) -> list[Span]:
        """Get child spans of a parent."""
        return [
            s for (inst, _), s in self._spans.items()
            if inst == installation_id and s.parent_span_id == span_id
        ]

    def _get(self, installation_id: str, span_id: str) -> Span:
        key = (installation_id, span_id)
        span = self._spans.get(key)
        if span is None:
            raise KeyError(f"Span {span_id} not found")
        return span
