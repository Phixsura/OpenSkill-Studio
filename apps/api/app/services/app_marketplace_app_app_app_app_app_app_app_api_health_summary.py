"""API health summary — aggregate health across all API endpoints."""
from __future__ import annotations


def summarize_api_health(endpoints: list[dict]) -> dict:
    total = len(endpoints)
    healthy = sum(1 for e in endpoints if e.get("healthy", False))
    avg_latency = round(sum(e.get("latency_ms", 0) for e in endpoints) / max(total, 1), 1)
    avg_error_rate = round(sum(e.get("error_rate", 0) for e in endpoints) / max(total, 1), 2)
    slowest = max(endpoints, key=lambda e: e.get("latency_ms", 0)) if endpoints else None
    most_errors = max(endpoints, key=lambda e: e.get("error_rate", 0)) if endpoints else None
    overall = "healthy" if healthy == total else "degraded" if healthy > total * 0.8 else "critical"
    return {
        "total_endpoints": total, "healthy": healthy,
        "unhealthy": total - healthy,
        "health_pct": round(healthy / max(total, 1) * 100),
        "avg_latency_ms": avg_latency,
        "avg_error_rate": avg_error_rate,
        "overall": overall,
        "slowest": {"endpoint": slowest.get("path", ""), "latency_ms": slowest.get("latency_ms", 0)} if slowest else None,
        "most_errors": {"endpoint": most_errors.get("path", ""), "error_rate": most_errors.get("error_rate", 0)} if most_errors else None,
    }
