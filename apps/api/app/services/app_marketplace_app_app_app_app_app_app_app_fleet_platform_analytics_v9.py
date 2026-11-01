"""Fleet Platform Analytics v9 — track platform usage analytics."""
from __future__ import annotations
def fleet_platform_analytics_v9(metrics: list[dict]) -> dict:
    dau = sum(m.get("dau", 0) for m in metrics)
    api_calls = sum(m.get("api_calls", 0) for m in metrics)
    avg_latency = sum(m.get("avg_latency_ms", 0) for m in metrics) / len(metrics) if metrics else 0
    return {"metrics": len(metrics), "dau": dau, "api_calls": api_calls,
            "avg_latency_ms": round(avg_latency, 1), "healthy": avg_latency < 200}
