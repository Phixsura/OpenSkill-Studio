"""Request tracing correlator — correlate requests across services via trace IDs."""
from __future__ import annotations
from collections import defaultdict


def correlate_traces(spans: list[dict]) -> dict:
    by_trace: dict[str, list[dict]] = defaultdict(list)
    for s in spans:
        by_trace[s["trace_id"]].append(s)
    traces = []
    for tid, trace_spans in by_trace.items():
        sorted_spans = sorted(trace_spans, key=lambda s: s.get("start_ms", 0))
        total_ms = max(s.get("start_ms", 0) + s.get("duration_ms", 0) for s in trace_spans) - min(s.get("start_ms", 0) for s in trace_spans)
        services = list(set(s.get("service", "") for s in trace_spans))
        traces.append({"trace_id": tid, "spans": len(trace_spans),
                        "services": services, "duration_ms": round(total_ms, 1),
                        "root_service": sorted_spans[0].get("service", "")})
    return {"traces": sorted(traces, key=lambda t: -t["duration_ms"]),
            "total_traces": len(traces), "total_spans": len(spans)}


def find_slow_traces(traces: list[dict], threshold_ms: float = 1000) -> list[dict]:
    return [t for t in traces if t["duration_ms"] > threshold_ms]
