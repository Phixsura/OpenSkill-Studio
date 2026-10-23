"""API latency histogram — bucket latency measurements for visualization."""

import math


DEFAULT_BUCKETS_MS = [5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000, 10000]


def build_histogram(*, latencies_ms: list[float], buckets: list[float] | None = None) -> dict:
    bins = buckets or DEFAULT_BUCKETS_MS
    counts = {b: 0 for b in bins}
    counts[float("inf")] = 0
    for lat in latencies_ms:
        placed = False
        for b in bins:
            if lat <= b:
                counts[b] += 1
                placed = True
                break
        if not placed:
            counts[float("inf")] += 1
    total = len(latencies_ms)
    histogram = []
    for b in bins:
        histogram.append({"le": b, "count": counts[b],
                           "pct": round(counts[b] / max(total, 1) * 100, 1)})
    histogram.append({"le": "+Inf", "count": counts[float("inf")],
                       "pct": round(counts[float("inf")] / max(total, 1) * 100, 1)})
    avg = round(sum(latencies_ms) / max(total, 1), 1) if latencies_ms else 0
    p50_idx = int(total * 0.5)
    p99_idx = min(int(total * 0.99), total - 1)
    sorted_lat = sorted(latencies_ms)
    return {
        "histogram": histogram,
        "total": total,
        "avg_ms": avg,
        "p50_ms": sorted_lat[p50_idx] if sorted_lat else 0,
        "p99_ms": sorted_lat[p99_idx] if sorted_lat else 0,
        "min_ms": min(latencies_ms) if latencies_ms else 0,
        "max_ms": max(latencies_ms) if latencies_ms else 0,
    }
