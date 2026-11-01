"""Request rate analyzer — analyze request rates and detect spikes."""
from __future__ import annotations
import math


def analyze_rate(timestamps: list[float], window_seconds: int = 60) -> dict:
    if not timestamps:
        return {"rps": 0, "total": 0, "window": window_seconds}
    sorted_ts = sorted(timestamps)
    duration = sorted_ts[-1] - sorted_ts[0]
    rps = round(len(timestamps) / max(duration, 0.01), 2)
    # Detect spikes using windowed counting
    buckets: dict[int, int] = {}
    for ts in sorted_ts:
        bucket = int(ts) // window_seconds
        buckets[bucket] = buckets.get(bucket, 0) + 1
    avg_per_window = sum(buckets.values()) / max(len(buckets), 1)
    max_per_window = max(buckets.values()) if buckets else 0
    spike = max_per_window > avg_per_window * 3
    return {"rps": rps, "total": len(timestamps),
            "avg_per_window": round(avg_per_window, 1),
            "max_per_window": max_per_window, "spike_detected": spike}
