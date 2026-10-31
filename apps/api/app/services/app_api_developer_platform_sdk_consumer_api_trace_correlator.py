"""Consumer API Trace Correlation — distributed trace correlation with span linking."""
from __future__ import annotations

import secrets
import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class Span:
    span_id: str
    trace_id: str
    parent_span_id: str | None = None
    service_name: str = ""
    operation: str = ""
    start_time: float = 0.0
    duration_ms: float = 0.0
    status: str = "ok"
    tags: dict[str, str] = field(default_factory=dict)


@dataclass
class TraceCorrelator:
    """Correlate distributed traces with span linking and analysis."""

    _spans: dict[str, list[Span]] = field(default_factory=dict)  # trace_id -> spans

    def generate_trace_id(self) -> str:
        return secrets.token_hex(16)

    def generate_span_id(self) -> str:
        return secrets.token_hex(8)

    def record_span(self, span: Span) -> dict:
        self._spans.setdefault(span.trace_id, []).append(span)
        logger.info("span_recorded", trace_id=span.trace_id, span_id=span.span_id)
        return {"trace_id": span.trace_id, "span_id": span.span_id,
                "total_spans": len(self._spans[span.trace_id])}

    def get_trace(self, trace_id: str) -> dict | None:
        spans = self._spans.get(trace_id)
        if not spans:
            return None
        total_duration = max(s.start_time + s.duration_ms for s in spans) - min(s.start_time for s in spans)
        services = sorted(set(s.service_name for s in spans if s.service_name))
        errors = [s for s in spans if s.status == "error"]
        return {
            "trace_id": trace_id,
            "span_count": len(spans),
            "total_duration_ms": round(total_duration, 2),
            "services": services,
            "service_count": len(services),
            "has_errors": len(errors) > 0,
            "error_count": len(errors),
        }

    def get_span_tree(self, trace_id: str) -> list[dict]:
        spans = self._spans.get(trace_id, [])
        roots = [s for s in spans if s.parent_span_id is None]
        def build_tree(parent_id: str | None) -> list[dict]:
            children = [s for s in spans if s.parent_span_id == parent_id]
            return [
                {"span_id": s.span_id, "service": s.service_name,
                 "operation": s.operation, "duration_ms": s.duration_ms,
                 "status": s.status, "children": build_tree(s.span_id)}
                for s in sorted(children, key=lambda x: x.start_time)
            ]
        return build_tree(None)

    def find_critical_path(self, trace_id: str) -> list[dict]:
        spans = self._spans.get(trace_id, [])
        if not spans:
            return []
        # Sort by duration descending, pick longest chain
        sorted_spans = sorted(spans, key=lambda s: s.duration_ms, reverse=True)
        return [
            {"span_id": s.span_id, "service": s.service_name,
             "operation": s.operation, "duration_ms": s.duration_ms}
            for s in sorted_spans[:5]
        ]

    def correlate(self, trace_id_a: str, trace_id_b: str) -> dict:
        spans_a = self._spans.get(trace_id_a, [])
        spans_b = self._spans.get(trace_id_b, [])
        services_a = set(s.service_name for s in spans_a)
        services_b = set(s.service_name for s in spans_b)
        common = sorted(services_a & services_b)
        return {
            "trace_a": trace_id_a, "trace_b": trace_id_b,
            "common_services": common,
            "shared_service_count": len(common),
        }

    def list_traces(self, limit: int = 20) -> list[dict]:
        results = []
        for tid in list(self._spans.keys())[-limit:]:
            info = self.get_trace(tid)
            if info:
                results.append(info)
        return list(reversed(results))

    def get_stats(self) -> dict:
        total_spans = sum(len(v) for v in self._spans.values())
        all_services: set[str] = set()
        for spans in self._spans.values():
            for s in spans:
                if s.service_name:
                    all_services.add(s.service_name)
        return {
            "total_traces": len(self._spans),
            "total_spans": total_spans,
            "unique_services": len(all_services),
        }
