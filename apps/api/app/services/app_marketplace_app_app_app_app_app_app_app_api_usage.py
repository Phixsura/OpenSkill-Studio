"""API usage analytics — track endpoint usage patterns."""
from __future__ import annotations


def analyze_usage(requests: list[dict]) -> dict:
    by_endpoint: dict[str, int] = {}
    by_method: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total_latency = 0
    for r in requests:
        ep = f"{r.get('method', 'GET')} {r.get('path', '/')}"
        by_endpoint[ep] = by_endpoint.get(ep, 0) + 1
        by_method[r.get("method", "GET")] = by_method.get(r.get("method", "GET"), 0) + 1
        sc = str(r.get("status", 200))
        by_status[sc] = by_status.get(sc, 0) + 1
        total_latency += r.get("latency_ms", 0)
    total = len(requests)
    error_count = sum(v for k, v in by_status.items() if k.startswith("5"))
    top_endpoint = max(by_endpoint, key=by_endpoint.get) if by_endpoint else None
    return {"total_requests": total, "by_endpoint": by_endpoint, "by_method": by_method,
            "by_status": by_status, "avg_latency_ms": round(total_latency / max(total, 1)),
            "error_count": error_count, "error_rate_pct": round(error_count / max(total, 1) * 100, 1),
            "top_endpoint": top_endpoint}
