"""Endpoint performance tracker — per-endpoint latency, throughput, and error rate."""
from __future__ import annotations
import math


def track_performance(requests: list[dict]) -> dict:
    by_endpoint: dict[str, dict] = {}
    for r in requests:
        key = f"{r.get('method', 'GET')} {r.get('path', '/')}"
        if key not in by_endpoint:
            by_endpoint[key] = {"latencies": [], "errors": 0, "total": 0}
        by_endpoint[key]["latencies"].append(r.get("latency_ms", 0))
        by_endpoint[key]["total"] += 1
        if r.get("status_code", 200) >= 400:
            by_endpoint[key]["errors"] += 1
    results = []
    for endpoint, data in by_endpoint.items():
        lats = sorted(data["latencies"])
        n = len(lats)
        p50 = lats[n // 2] if n else 0
        p99 = lats[int(n * 0.99)] if n else 0
        avg = round(sum(lats) / max(n, 1), 1)
        error_rate = round(data["errors"] / max(data["total"], 1) * 100, 1)
        results.append({
            "endpoint": endpoint, "total": data["total"],
            "avg_ms": avg, "p50_ms": p50, "p99_ms": p99,
            "error_rate": error_rate, "errors": data["errors"],
            "health": "poor" if error_rate > 5 or p99 > 2000 else "ok" if error_rate > 1 or p99 > 500 else "good",
        })
    results.sort(key=lambda x: -x["p99_ms"])
    return {"endpoints": results, "total_endpoints": len(results),
            "total_requests": sum(r["total"] for r in results)}
