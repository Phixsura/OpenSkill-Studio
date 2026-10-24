"""API traffic analyzer — analyze request patterns and trends."""
from __future__ import annotations


def analyze_traffic(requests: list[dict]) -> dict:
    by_method: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_path: dict[str, int] = {}
    total_latency = 0
    for r in requests:
        by_method[r.get("method", "GET")] = by_method.get(r.get("method", "GET"), 0) + 1
        status = str(r.get("status", 200))
        by_status[status] = by_status.get(status, 0) + 1
        by_path[r.get("path", "/")] = by_path.get(r.get("path", "/"), 0) + 1
        total_latency += r.get("latency_ms", 0)
    total = len(requests)
    errors = sum(v for k, v in by_status.items() if k.startswith("5"))
    top_path = max(by_path, key=by_path.get) if by_path else None
    return {"total_requests": total, "by_method": by_method, "by_status": by_status,
            "top_path": top_path, "top_path_count": by_path.get(top_path, 0) if top_path else 0,
            "avg_latency_ms": round(total_latency / max(total, 1)),
            "error_count": errors, "error_pct": round(errors / max(total, 1) * 100, 1)}
