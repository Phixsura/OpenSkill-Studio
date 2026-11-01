"""Request timeout analytics — analyze timeout patterns across services."""
from __future__ import annotations
from collections import defaultdict


def analyze_timeouts(requests: list[dict], timeout_ms: float = 5000) -> dict:
    by_endpoint: dict[str, dict] = defaultdict(lambda: {"total": 0, "timeouts": 0})
    for r in requests:
        ep = r.get("endpoint", "/")
        by_endpoint[ep]["total"] += 1
        if r.get("duration_ms", 0) >= timeout_ms:
            by_endpoint[ep]["timeouts"] += 1
    endpoints = []
    for ep, data in sorted(by_endpoint.items(), key=lambda x: -x[1]["timeouts"]):
        if data["timeouts"] > 0:
            rate = round(data["timeouts"] / max(data["total"], 1) * 100, 1)
            endpoints.append({"endpoint": ep, "timeouts": data["timeouts"],
                               "total": data["total"], "timeout_rate": rate})
    total_timeouts = sum(e["timeouts"] for e in endpoints)
    return {"endpoints": endpoints, "total_timeouts": total_timeouts,
            "total_requests": len(requests), "threshold_ms": timeout_ms,
            "overall_timeout_rate": round(total_timeouts / max(len(requests), 1) * 100, 2)}
