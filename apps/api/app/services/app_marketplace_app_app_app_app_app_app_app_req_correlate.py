"""Request correlation engine — correlate requests across services."""
from __future__ import annotations
import secrets


def generate_correlation_id() -> str:
    return f"cor_{secrets.token_urlsafe(16)}"


def correlate_requests(spans: list[dict]) -> dict:
    by_correlation: dict[str, list[dict]] = {}
    for s in spans:
        cid = s.get("correlation_id", "unknown")
        by_correlation.setdefault(cid, []).append(s)
    traces = []
    for cid, req_spans in by_correlation.items():
        total_ms = sum(sp.get("duration_ms", 0) for sp in req_spans)
        services = sorted({sp.get("service", "") for sp in req_spans})
        traces.append({"correlation_id": cid, "span_count": len(req_spans),
                        "total_ms": round(total_ms, 1), "services": services})
    return {"traces": traces, "total_traces": len(traces),
            "total_spans": len(spans)}


def find_slow_traces(traces: list[dict], threshold_ms: float = 1000) -> list[dict]:
    return sorted([t for t in traces if t["total_ms"] >= threshold_ms],
                  key=lambda t: -t["total_ms"])
