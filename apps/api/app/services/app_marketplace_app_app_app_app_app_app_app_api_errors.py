"""API error tracker — track and categorize API errors for debugging."""
from __future__ import annotations


def categorize_errors(errors: list[dict]) -> dict:
    by_status: dict[int, int] = {}
    by_endpoint: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for e in errors:
        status = e.get("status", 500)
        endpoint = e.get("endpoint", "unknown")
        etype = e.get("error_type", "unknown")
        by_status[status] = by_status.get(status, 0) + 1
        by_endpoint[endpoint] = by_endpoint.get(endpoint, 0) + 1
        by_type[etype] = by_type.get(etype, 0) + 1
    total = len(errors)
    top_endpoint = max(by_endpoint, key=by_endpoint.get) if by_endpoint else None
    return {
        "total": total, "by_status": dict(sorted(by_status.items())),
        "by_endpoint": dict(sorted(by_endpoint.items(), key=lambda x: -x[1])),
        "by_type": dict(sorted(by_type.items(), key=lambda x: -x[1])),
        "top_endpoint": top_endpoint,
        "client_errors": sum(v for k, v in by_status.items() if 400 <= k < 500),
        "server_errors": sum(v for k, v in by_status.items() if k >= 500),
    }
