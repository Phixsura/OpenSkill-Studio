"""API latency profiler — analyze latency distribution across endpoints."""

import math


def compute_latency_percentiles(*, latencies: list[int]) -> dict:
    if not latencies:
        return {"p50": 0, "p90": 0, "p95": 0, "p99": 0, "avg": 0, "min": 0, "max": 0}
    s = sorted(latencies)
    n = len(s)
    return {
        "p50": s[int(n * 0.50)], "p90": s[int(n * 0.90)], "p95": s[min(int(n * 0.95), n - 1)],
        "p99": s[min(int(n * 0.99), n - 1)], "avg": round(sum(s) / n),
        "min": s[0], "max": s[-1], "count": n,
    }


def identify_slow_endpoints(*, endpoint_latencies: dict[str, list[int]], threshold_ms: int = 500) -> list[dict]:
    slow = []
    for path, lats in endpoint_latencies.items():
        percentiles = compute_latency_percentiles(latencies=lats)
        if percentiles["p95"] > threshold_ms:
            slow.append({"path": path, "p95_ms": percentiles["p95"], "avg_ms": percentiles["avg"],
                          "call_count": len(lats)})
    return sorted(slow, key=lambda x: -x["p95_ms"])


def compute_latency_budget(*, target_p99_ms: int, current_p99_ms: int) -> dict:
    remaining = target_p99_ms - current_p99_ms
    return {"target_p99_ms": target_p99_ms, "current_p99_ms": current_p99_ms,
            "remaining_ms": max(0, remaining), "within_budget": remaining >= 0,
            "usage_pct": round(current_p99_ms / max(target_p99_ms, 1) * 100, 1)}
