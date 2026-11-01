"""API health report — comprehensive API performance report."""
from __future__ import annotations


def generate_api_report(endpoints: list[dict]) -> dict:
    total = len(endpoints)
    healthy = sum(1 for e in endpoints if e.get("error_rate", 0) < 1 and e.get("p99_ms", 0) < 500)
    degraded = sum(1 for e in endpoints if 1 <= e.get("error_rate", 0) < 5 or 500 <= e.get("p99_ms", 0) < 1000)
    unhealthy = total - healthy - degraded
    
    total_rps = sum(e.get("rps", 0) for e in endpoints)
    avg_latency = round(sum(e.get("p99_ms", 0) for e in endpoints) / max(total, 1))
    avg_error = round(sum(e.get("error_rate", 0) for e in endpoints) / max(total, 1), 2)
    
    grade = "A" if healthy / max(total, 1) >= 0.95 else "B" if healthy / max(total, 1) >= 0.8 else "C"
    return {"total_endpoints": total, "healthy": healthy, "degraded": degraded,
            "unhealthy": unhealthy, "total_rps": total_rps,
            "avg_latency_ms": avg_latency, "avg_error_rate": avg_error,
            "grade": grade, "health_pct": round(healthy / max(total, 1) * 100)}
