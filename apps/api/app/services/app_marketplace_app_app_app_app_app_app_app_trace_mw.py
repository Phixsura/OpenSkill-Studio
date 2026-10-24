"""Request tracing middleware — inject trace context into requests."""
from __future__ import annotations
import secrets


def create_trace_context() -> dict:
    trace_id = secrets.token_hex(16)
    span_id = secrets.token_hex(8)
    return {"trace_id": trace_id, "span_id": span_id, "parent_id": None,
            "sampled": True, "baggage": {},
            "header": f"00-{trace_id}-{span_id}-01"}


def create_child_span(parent: dict, operation: str) -> dict:
    span_id = secrets.token_hex(8)
    return {"trace_id": parent["trace_id"], "span_id": span_id,
            "parent_id": parent["span_id"], "operation": operation,
            "sampled": parent["sampled"]}


def parse_traceparent(header: str) -> dict:
    parts = header.split("-")
    if len(parts) != 4:
        return {"valid": False, "error": "invalid format"}
    return {"valid": True, "version": parts[0], "trace_id": parts[1],
            "span_id": parts[2], "flags": parts[3],
            "sampled": parts[3] == "01"}
