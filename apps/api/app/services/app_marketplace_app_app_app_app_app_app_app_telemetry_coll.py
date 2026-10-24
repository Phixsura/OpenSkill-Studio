"""Telemetry collector — collect and aggregate telemetry data."""
from __future__ import annotations

_spans: list[dict] = []


def record_span(trace_id: str, span_id: str, operation: str, duration_ms: float,
                status: str = "ok", tags: dict | None = None) -> dict:
    span = {"trace_id": trace_id, "span_id": span_id, "operation": operation,
            "duration_ms": round(duration_ms, 2), "status": status,
            "tags": tags or {}}
    _spans.append(span)
    return span


def aggregate_spans(operation: str | None = None) -> dict:
    filtered = [s for s in _spans if not operation or s["operation"] == operation]
    if not filtered:
        return {"count": 0, "avg_ms": 0, "p50_ms": 0, "p99_ms": 0, "error_count": 0}
    durations = sorted(s["duration_ms"] for s in filtered)
    errors = sum(1 for s in filtered if s["status"] == "error")
    p50 = durations[len(durations) // 2]
    p99 = durations[int(len(durations) * 0.99)]
    return {"count": len(filtered), "avg_ms": round(sum(durations) / len(durations), 2),
            "p50_ms": p50, "p99_ms": p99, "error_count": errors,
            "error_rate": round(errors / len(filtered) * 100, 2)}


def top_operations(limit: int = 10) -> list[dict]:
    by_op: dict[str, list[float]] = {}
    for s in _spans:
        by_op.setdefault(s["operation"], []).append(s["duration_ms"])
    results = []
    for op, durs in by_op.items():
        results.append({"operation": op, "count": len(durs),
                        "avg_ms": round(sum(durs) / len(durs), 2)})
    return sorted(results, key=lambda x: -x["count"])[:limit]


def clear_spans() -> None:
    _spans.clear()
