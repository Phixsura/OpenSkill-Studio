"""Distributed trace analyzer — analyze trace data for bottlenecks."""
from __future__ import annotations


def analyze_trace(spans: list[dict]) -> dict:
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    sorted_spans = sorted(spans, key=lambda s: -s.get("duration_ms", 0))
    bottleneck = sorted_spans[0] if sorted_spans else None
    services = sorted({s.get("service", "") for s in spans})
    error_spans = [s for s in spans if s.get("status") == "error"]
    return {"span_count": len(spans), "total_ms": round(total_ms, 1),
            "bottleneck": bottleneck["operation"] if bottleneck else None,
            "bottleneck_ms": bottleneck["duration_ms"] if bottleneck else 0,
            "services": services, "service_count": len(services),
            "error_spans": len(error_spans), "has_errors": len(error_spans) > 0}


def trace_summary(traces: list[dict]) -> dict:
    avg_duration = round(sum(t["total_ms"] for t in traces) / max(len(traces), 1), 1)
    with_errors = sum(1 for t in traces if t.get("has_errors"))
    return {"total_traces": len(traces), "avg_duration_ms": avg_duration,
            "with_errors": with_errors, "error_pct": round(with_errors / max(len(traces), 1) * 100)}
