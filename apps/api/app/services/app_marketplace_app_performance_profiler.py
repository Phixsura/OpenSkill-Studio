"""Performance profiler — analyze app response times and bottlenecks."""


def profile_endpoints(*, endpoints: list[dict]) -> dict:
    results = []
    for ep in endpoints:
        p50 = ep.get("p50_ms", 0)
        p95 = ep.get("p95_ms", 0)
        p99 = ep.get("p99_ms", 0)
        rps = ep.get("requests_per_sec", 0)
        slow = p95 > 500
        results.append({
            "endpoint": ep["path"],
            "method": ep.get("method", "GET"),
            "p50_ms": p50, "p95_ms": p95, "p99_ms": p99,
            "requests_per_sec": rps,
            "is_slow": slow,
            "score": max(0, 100 - int(p95 / 10)),
        })
    results.sort(key=lambda x: x["p95_ms"], reverse=True)
    slow_count = sum(1 for r in results if r["is_slow"])
    avg_p95 = round(sum(r["p95_ms"] for r in results) / max(len(results), 1), 1)
    return {
        "endpoints": results,
        "total": len(results),
        "slow_endpoints": slow_count,
        "avg_p95_ms": avg_p95,
        "overall_score": max(0, 100 - slow_count * 15),
    }
