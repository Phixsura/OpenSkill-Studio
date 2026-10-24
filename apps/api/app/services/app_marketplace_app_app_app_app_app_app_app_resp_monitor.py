"""API response time monitor — real-time endpoint response tracking."""
from __future__ import annotations


def analyze_response_times(samples: list[dict]) -> dict:
    by_endpoint: dict[str, list[float]] = {}
    for s in samples:
        ep = s.get("endpoint", "unknown")
        by_endpoint.setdefault(ep, []).append(s.get("latency_ms", 0))
    results = []
    for ep, latencies in sorted(by_endpoint.items()):
        sorted_lat = sorted(latencies)
        n = len(sorted_lat)
        avg = round(sum(sorted_lat) / n, 1)
        p50 = sorted_lat[n // 2]
        p99 = sorted_lat[int(n * 0.99)] if n > 1 else sorted_lat[0]
        status = "fast" if p99 < 200 else "ok" if p99 < 500 else "slow"
        results.append({"endpoint": ep, "count": n, "avg_ms": avg,
                          "p50_ms": p50, "p99_ms": p99, "status": status})
    overall_avg = round(sum(s.get("latency_ms", 0) for s in samples) / max(len(samples), 1), 1)
    return {"endpoints": results, "total_samples": len(samples),
            "overall_avg_ms": overall_avg,
            "slowest": max(results, key=lambda r: r["p99_ms"])["endpoint"] if results else None}
