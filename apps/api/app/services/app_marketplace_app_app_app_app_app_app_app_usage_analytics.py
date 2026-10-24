"""API usage analytics — aggregate API usage metrics per endpoint."""
from __future__ import annotations
from collections import defaultdict


def aggregate_usage(requests: list[dict]) -> dict:
    by_endpoint: dict[str, dict] = defaultdict(lambda: {"count": 0, "total_ms": 0, "errors": 0})
    by_status: dict[int, int] = defaultdict(int)
    for r in requests:
        ep = r["endpoint"]
        by_endpoint[ep]["count"] += 1
        by_endpoint[ep]["total_ms"] += r.get("latency_ms", 0)
        if r.get("status", 200) >= 400:
            by_endpoint[ep]["errors"] += 1
        by_status[r.get("status", 200)] += 1
    endpoints = []
    for ep, data in sorted(by_endpoint.items(), key=lambda x: -x[1]["count"]):
        avg = round(data["total_ms"] / max(data["count"], 1), 1)
        err_rate = round(data["errors"] / max(data["count"], 1) * 100, 2)
        endpoints.append({"endpoint": ep, "count": data["count"],
                          "avg_ms": avg, "error_rate": err_rate})
    return {"endpoints": endpoints, "total_requests": len(requests),
            "status_codes": dict(by_status), "unique_endpoints": len(endpoints)}


def top_consumers(requests: list[dict], limit: int = 5) -> list[dict]:
    by_user: dict[str, int] = defaultdict(int)
    for r in requests:
        by_user[r.get("user_id", "anon")] += 1
    sorted_users = sorted(by_user.items(), key=lambda x: -x[1])[:limit]
    return [{"user_id": u, "count": c} for u, c in sorted_users]
