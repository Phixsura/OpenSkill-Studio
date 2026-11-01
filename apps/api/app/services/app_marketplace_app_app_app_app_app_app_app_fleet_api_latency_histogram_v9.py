"""Fleet API Latency Histogram v9 — track latency distribution buckets."""
from __future__ import annotations
def fleet_api_latency_histogram_v9(endpoints: list[dict]) -> dict:
    under_10ms = sum(e.get("under_10ms_pct", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    under_50ms = sum(e.get("under_50ms_pct", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    under_100ms = sum(e.get("under_100ms_pct", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "under_10ms_pct": round(under_10ms, 1),
            "under_50ms_pct": round(under_50ms, 1), "under_100ms_pct": round(under_100ms, 1),
            "healthy": under_100ms > 95}
