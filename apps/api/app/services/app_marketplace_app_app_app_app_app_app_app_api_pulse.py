"""API health pulse — real-time API health heartbeat."""
from __future__ import annotations
import time


def pulse_check(endpoints: list[dict]) -> dict:
    healthy = sum(1 for e in endpoints if e.get("status") == "healthy")
    total = len(endpoints)
    avg_latency = round(sum(e.get("latency_ms", 0) for e in endpoints) / max(total, 1))
    total_rps = sum(e.get("rps", 0) for e in endpoints)
    error_count = sum(e.get("errors", 0) for e in endpoints)
    pulse = "strong" if healthy == total and avg_latency < 200 else "weak" if healthy > total * 0.5 else "critical"
    return {"healthy": healthy, "total": total, "avg_latency_ms": avg_latency,
            "total_rps": total_rps, "error_count": error_count,
            "pulse": pulse, "timestamp": time.time()}


def pulse_trend(pulses: list[dict]) -> dict:
    if len(pulses) < 2:
        return {"trend": "insufficient"}
    recent_healthy = pulses[-1].get("healthy", 0)
    prev_healthy = pulses[-2].get("healthy", 0)
    return {"improving": recent_healthy > prev_healthy,
            "stable": recent_healthy == prev_healthy,
            "degrading": recent_healthy < prev_healthy}
