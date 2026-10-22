"""Distributed tracing — trace requests across app services and webhooks."""

import hashlib
import time


def create_trace(*, trace_id: str | None = None) -> dict:
    tid = trace_id or hashlib.sha256(str(time.time()).encode()).hexdigest()[:16]
    return {"trace_id": tid, "spans": [], "status": "active"}


def add_span(*, trace: dict, service: str, operation: str, duration_ms: int,
                status: str = "ok", parent_span_id: str | None = None) -> dict:
    span_id = hashlib.sha256(f"{trace['trace_id']}:{len(trace['spans'])}".encode()).hexdigest()[:8]
    span = {"span_id": span_id, "service": service, "operation": operation,
            "duration_ms": duration_ms, "status": status, "parent_span_id": parent_span_id}
    return {**trace, "spans": trace["spans"] + [span]}


def compute_trace_summary(*, trace: dict) -> dict:
    spans = trace.get("spans", [])
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    services = list(set(s.get("service") for s in spans))
    errors = [s for s in spans if s.get("status") == "error"]
    return {"trace_id": trace["trace_id"], "span_count": len(spans),
            "total_duration_ms": total_ms, "services": services,
            "has_errors": len(errors) > 0, "error_count": len(errors)}
