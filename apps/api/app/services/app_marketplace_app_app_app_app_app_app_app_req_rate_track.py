"""Request rate tracker — monitor request rates by endpoint and status."""
from __future__ import annotations


def track_request_rates(endpoints: list[dict]) -> dict:
    total_rps = 0
    by_status: dict[str, int] = {}
    by_endpoint: dict[str, int] = {}
    for e in endpoints:
        rps = e.get("rps", 0)
        total_rps += rps
        by_endpoint[e.get("path", "/")] = rps
        for status, count in e.get("status_counts", {}).items():
            by_status[status] = by_status.get(status, 0) + count
    error_rps = sum(v for k, v in by_status.items() if k.startswith("5"))
    success_rps = sum(v for k, v in by_status.items() if k.startswith("2"))
    return {"total_rps": total_rps, "by_status": by_status, "by_endpoint": by_endpoint,
            "error_rps": error_rps, "success_rps": success_rps,
            "error_pct": round(error_rps / max(total_rps, 1) * 100, 1),
            "endpoint_count": len(endpoints)}
