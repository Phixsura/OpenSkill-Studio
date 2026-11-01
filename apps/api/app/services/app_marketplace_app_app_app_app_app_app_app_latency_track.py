"""API latency tracker — track and bucket latency measurements."""
from __future__ import annotations

def bucket_latencies(latencies: list[float]) -> dict:
    buckets = {"<10ms": 0, "10-50ms": 0, "50-100ms": 0, "100-500ms": 0, ">500ms": 0}
    for l in latencies:
        if l < 10: buckets["<10ms"] += 1
        elif l < 50: buckets["10-50ms"] += 1
        elif l < 100: buckets["50-100ms"] += 1
        elif l < 500: buckets["100-500ms"] += 1
        else: buckets[">500ms"] += 1
    total = len(latencies)
    return {"buckets": buckets, "total": total,
            "pct": {k: round(v/max(total,1)*100, 1) for k, v in buckets.items()}}
