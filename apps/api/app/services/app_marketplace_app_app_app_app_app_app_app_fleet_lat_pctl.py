"""Fleet API latency percentiles — p50/p95/p99 across fleet."""
from __future__ import annotations
def fleet_latency_percentiles(samples: list[float]) -> dict:
    if not samples:
        return {"p50": 0, "p95": 0, "p99": 0, "count": 0}
    s = sorted(samples)
    n = len(s)
    return {"p50": s[int(n * 0.5)], "p95": s[min(int(n * 0.95), n - 1)],
            "p99": s[min(int(n * 0.99), n - 1)], "count": n}
