"""Mesh health aggregator — aggregate health across all mesh services."""
from __future__ import annotations


def aggregate_mesh_health(services: list[dict]) -> dict:
    healthy = sum(1 for s in services if s.get("health") == "healthy")
    degraded = sum(1 for s in services if s.get("health") == "degraded")
    down = sum(1 for s in services if s.get("health") == "down")
    total = len(services)
    avg_latency = round(sum(s.get("avg_latency_ms", 0) for s in services) / max(total, 1), 1)
    avg_error = round(sum(s.get("error_rate_pct", 0) for s in services) / max(total, 1), 2)
    overall = "healthy" if down == 0 and degraded == 0 else ("critical" if down > total * 0.3 else "degraded")
    mtls_count = sum(1 for s in services if s.get("mtls"))
    return {"overall": overall, "total": total, "healthy": healthy,
            "degraded": degraded, "down": down,
            "avg_latency_ms": avg_latency, "avg_error_rate_pct": avg_error,
            "mtls_coverage_pct": round(mtls_count / max(total, 1) * 100, 1),
            "health_pct": round(healthy / max(total, 1) * 100, 1)}
