"""Fleet API Latency Tracker v9 — track p50/p95/p99 latency per endpoint."""
from __future__ import annotations
def fleet_api_latency_tracker_v9(endpoints: list[dict]) -> dict:
    avg_p50 = sum(e.get("p50_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    avg_p95 = sum(e.get("p95_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    avg_p99 = sum(e.get("p99_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    slow = [e for e in endpoints if e.get("p99_ms", 0) > 500]
    return {"endpoints": len(endpoints), "avg_p50_ms": round(avg_p50, 1), "avg_p95_ms": round(avg_p95, 1),
            "avg_p99_ms": round(avg_p99, 1), "slow_endpoints": len(slow), "healthy": len(slow) == 0}
