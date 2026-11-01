"""API client error tracker — track 4xx errors from client requests."""
from __future__ import annotations
from collections import defaultdict


def track_client_errors(errors: list[dict]) -> dict:
    by_status: dict[int, int] = defaultdict(int)
    by_endpoint: dict[str, int] = defaultdict(int)
    for e in errors:
        by_status[e.get("status", 400)] += 1
        by_endpoint[e.get("endpoint", "/")] += 1
    top_endpoints = sorted(by_endpoint.items(), key=lambda x: -x[1])[:5]
    return {"total": len(errors), "by_status": dict(by_status),
            "top_endpoints": [{"endpoint": k, "count": v} for k, v in top_endpoints],
            "unique_endpoints": len(by_endpoint)}


def client_error_rate(total_requests: int, client_errors: int) -> dict:
    rate = round(client_errors / max(total_requests, 1) * 100, 2)
    return {"rate_pct": rate, "total_requests": total_requests,
            "client_errors": client_errors, "healthy": rate < 5}
