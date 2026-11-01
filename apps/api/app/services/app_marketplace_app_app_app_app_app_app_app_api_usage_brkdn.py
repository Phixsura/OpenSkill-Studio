"""API usage breakdown — per-endpoint usage analysis for app developers."""
from __future__ import annotations


def compute_usage_breakdown(requests: list[dict]) -> dict:
    by_endpoint: dict[str, dict] = {}
    total = len(requests)
    for r in requests:
        ep = f"{r.get('method', 'GET')} {r.get('path', '/')}"
        if ep not in by_endpoint:
            by_endpoint[ep] = {"count": 0, "total_ms": 0, "errors": 0}
        by_endpoint[ep]["count"] += 1
        by_endpoint[ep]["total_ms"] += r.get("duration_ms", 0)
        if r.get("status", 200) >= 400:
            by_endpoint[ep]["errors"] += 1
    breakdown = []
    for ep, data in sorted(by_endpoint.items(), key=lambda x: -x[1]["count"]):
        avg_ms = round(data["total_ms"] / max(data["count"], 1), 1)
        error_pct = round(data["errors"] / max(data["count"], 1) * 100, 1)
        breakdown.append({"endpoint": ep, "count": data["count"],
                           "pct": round(data["count"] / max(total, 1) * 100, 1),
                           "avg_ms": avg_ms, "errors": data["errors"], "error_pct": error_pct})
    return {"breakdown": breakdown, "total_requests": total,
            "unique_endpoints": len(breakdown)}
