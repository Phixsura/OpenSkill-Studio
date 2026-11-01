"""Slow endpoint finder — find endpoints exceeding latency thresholds."""
from __future__ import annotations
from collections import defaultdict


def find_slow_endpoints(requests: list[dict], threshold_ms: float = 200) -> dict:
    by_ep: dict[str, list[float]] = defaultdict(list)
    for r in requests:
        by_ep[r.get("endpoint", "/")].append(r.get("latency_ms", 0))
    slow = []
    for ep, latencies in by_ep.items():
        avg = sum(latencies) / len(latencies)
        s = sorted(latencies)
        p99 = s[int(len(s) * 0.99)]
        if p99 > threshold_ms:
            slow.append({"endpoint": ep, "avg_ms": round(avg, 1), "p99_ms": p99,
                          "samples": len(latencies)})
    slow.sort(key=lambda e: -e["p99_ms"])
    return {"slow_endpoints": slow, "total_endpoints": len(by_ep),
            "slow_count": len(slow), "threshold_ms": threshold_ms}
