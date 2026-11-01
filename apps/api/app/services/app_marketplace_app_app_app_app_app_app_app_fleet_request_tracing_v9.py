"""Fleet Request Tracing v9 — track end-to-end request flow tracing."""
from __future__ import annotations
def fleet_request_tracing_v9(traces: list[dict]) -> dict:
    sampled = [t for t in traces if t.get("sampled")]
    avg_spans = sum(t.get("spans", 0) for t in traces) / len(traces) if traces else 0
    errors = [t for t in traces if t.get("has_error")]
    return {"traces": len(traces), "sampled": len(sampled), "avg_spans": round(avg_spans, 1),
            "errors": len(errors), "healthy": len(errors) == 0}
