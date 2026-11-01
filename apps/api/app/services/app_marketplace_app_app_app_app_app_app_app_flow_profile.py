"""Request flow profiler — profile request flow through service chain."""
from __future__ import annotations


def profile_flow(spans: list[dict]) -> dict:
    total_ms = sum(s.get("duration_ms", 0) for s in spans)
    bottleneck = max(spans, key=lambda s: s.get("duration_ms", 0)) if spans else None
    overhead_ms = 0
    for i, s in enumerate(spans):
        if i > 0:
            gap = s.get("start_ms", 0) - (spans[i-1].get("start_ms", 0) + spans[i-1].get("duration_ms", 0))
            overhead_ms += max(0, gap)
    efficiency = round((total_ms - overhead_ms) / max(total_ms, 0.01) * 100, 1) if total_ms > 0 else 100
    return {"total_ms": round(total_ms, 1), "spans": len(spans),
            "bottleneck": bottleneck.get("service", "") if bottleneck else "",
            "bottleneck_ms": bottleneck.get("duration_ms", 0) if bottleneck else 0,
            "overhead_ms": round(overhead_ms, 1), "efficiency_pct": efficiency}
