"""Error correlation engine — correlate errors across services."""
from __future__ import annotations
from collections import defaultdict


def correlate_errors(errors: list[dict]) -> dict:
    by_trace: dict[str, list[dict]] = defaultdict(list)
    for e in errors:
        tid = e.get("trace_id", "unknown")
        by_trace[tid].append({"service": e["service"], "error": e["error"],
                               "timestamp": e.get("timestamp", 0)})
    cascades = []
    for tid, errs in by_trace.items():
        if len(errs) > 1:
            cascades.append({"trace_id": tid, "services": [e["service"] for e in errs],
                             "error_count": len(errs),
                             "root_service": errs[0]["service"]})
    return {"total_errors": len(errors), "correlated_cascades": len(cascades),
            "cascades": sorted(cascades, key=lambda c: -c["error_count"]),
            "unique_traces": len(by_trace)}
