"""Dependency lag detector — detect latency spikes between dependent services."""
from __future__ import annotations
from collections import defaultdict


def detect_lag(calls: list[dict], threshold_ms: float = 200) -> dict:
    by_pair: dict[str, list[float]] = defaultdict(list)
    for c in calls:
        key = f"{c['source']}→{c['destination']}"
        by_pair[key].append(c.get("latency_ms", 0))
    lagging = []
    for pair, latencies in by_pair.items():
        avg = sum(latencies) / len(latencies)
        if avg > threshold_ms:
            src, dst = pair.split("→")
            lagging.append({"source": src, "destination": dst,
                            "avg_ms": round(avg, 1), "calls": len(latencies),
                            "max_ms": max(latencies)})
    return {"lagging_pairs": sorted(lagging, key=lambda l: -l["avg_ms"]),
            "total_pairs": len(by_pair), "lagging_count": len(lagging),
            "threshold_ms": threshold_ms}
