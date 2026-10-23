"""Health check aggregator — combine multiple service health checks."""
from __future__ import annotations


def aggregate_health(checks: list[dict]) -> dict:
    results = []
    healthy = 0
    for c in checks:
        status = c.get("status", "unknown")
        latency = c.get("latency_ms", 0)
        is_healthy = status == "healthy" and latency < c.get("timeout_ms", 5000)
        if is_healthy:
            healthy += 1
        results.append({
            "service": c["service"],
            "status": "healthy" if is_healthy else "unhealthy",
            "latency_ms": latency,
            "message": c.get("message", ""),
        })
    total = len(results)
    pct = round(healthy / max(total, 1) * 100)
    overall = "healthy" if pct == 100 else "degraded" if pct >= 50 else "outage"
    return {"checks": results, "total": total, "healthy": healthy,
            "unhealthy": total - healthy, "health_pct": pct, "overall": overall}
