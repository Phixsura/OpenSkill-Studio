"""API Consumer Request Trace Exporter — export distributed traces."""
from __future__ import annotations
from dataclasses import dataclass, field
import json
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
    parent_span_id: str = ""

@dataclass
class TraceExport:
    export_id: str
    format: str = "otlp"  # "otlp", "jaeger", "zipkin"
    span_count: int = 0

VALID_FORMATS = {"otlp", "jaeger", "zipkin"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRequestTraceExporter:
    def __init__(self) -> None:
        self._spans: dict[str, list[TraceSpan]] = {}
        self._exports: dict[str, list[TraceExport]] = {}

    def record_span(self, installation_id: str, span: TraceSpan) -> TraceSpan:
        if not installation_id: raise ValueError("installation_id is required")
        self._spans.setdefault(installation_id, []).append(span)
        return span

    def export_traces(self, installation_id: str, export_id: str, fmt: str = "otlp") -> TraceExport:
        if fmt not in VALID_FORMATS: raise ValueError(f"Invalid format: {fmt}")
        spans = self._spans.get(installation_id, [])
        export = TraceExport(export_id=export_id, format=fmt, span_count=len(spans))
        self._exports.setdefault(installation_id, []).append(export)
        return export

    def span_count(self, installation_id: str) -> int:
        return len(self._spans.get(installation_id, []))

    def trace_ids(self, installation_id: str) -> list[str]:
        return list({s.trace_id for s in self._spans.get(installation_id, [])})

    def error_spans(self, installation_id: str) -> list[TraceSpan]:
        return [s for s in self._spans.get(installation_id, []) if s.status == "error"]
