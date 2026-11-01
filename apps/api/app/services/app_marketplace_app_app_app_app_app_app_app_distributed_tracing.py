"""Distributed tracing — trace requests across services with span hierarchy."""
from __future__ import annotations
import secrets


def create_trace(*, service: str, operation: str) -> dict:
    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return {"trace_id": trace_id, "root_span": span_id,
            "service": service, "operation": operation, "spans": [
                {"span_id": span_id, "parent": None, "service": service,
                 "operation": operation, "duration_ms": 0, "status": "active"}
            ]}


def add_span(trace: dict, *, parent_span: str, service: str,
             operation: str, duration_ms: int = 0, status: str = "ok") -> dict:
    span_id = secrets.token_hex(8)
    span = {"span_id": span_id, "parent": parent_span, "service": service,
            "operation": operation, "duration_ms": duration_ms, "status": status}
    trace["spans"].append(span)
    return span


def analyze_trace(trace: dict) -> dict:
    spans = trace.get("spans", [])
    total_duration = max((s["duration_ms"] for s in spans), default=0)
    services = list({s["service"] for s in spans})
    errors = [s for s in spans if s["status"] == "error"]
    bottleneck = max(spans, key=lambda s: s["duration_ms"]) if spans else None
    return {
        "trace_id": trace["trace_id"],
        "span_count": len(spans),
        "total_duration_ms": total_duration,
        "duration_display": f"{total_duration}ms",
        "services": services, "service_count": len(services),
        "error_count": len(errors),
        "has_errors": len(errors) > 0,
        "bottleneck": {"service": bottleneck["service"], "operation": bottleneck["operation"],
                        "duration_ms": bottleneck["duration_ms"]} if bottleneck else None,
    }
