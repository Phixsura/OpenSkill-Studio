"""Fleet API Analytics v9 — track API usage patterns and top consumers."""
from __future__ import annotations
def fleet_api_analytics_v9(endpoints: list[dict]) -> dict:
    total_calls = sum(e.get("calls_today", 0) for e in endpoints)
    top_consumer = max(endpoints, key=lambda e: e.get("calls_today", 0), default={}).get("consumer", "unknown")
    avg_latency = sum(e.get("avg_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "calls_today": total_calls, "top_consumer": top_consumer,
            "avg_latency_ms": round(avg_latency, 1), "healthy": avg_latency < 200}
