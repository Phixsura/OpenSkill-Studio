"""Service mesh observability summary — unified mesh overview."""
from __future__ import annotations


def mesh_summary(services: list[dict], traffic: dict, health: dict) -> dict:
    total_services = len(services)
    healthy = sum(1 for s in services if s.get("healthy"))
    total_rps = traffic.get("total_rps", 0)
    error_rate = traffic.get("error_rate_pct", 0)
    mtls_pct = round(sum(1 for s in services if s.get("mtls")) / max(total_services, 1) * 100, 1)
    overall = "healthy" if healthy == total_services and error_rate < 1 else (
        "degraded" if healthy > total_services * 0.5 else "critical")
    return {"overall": overall, "total_services": total_services,
            "healthy": healthy, "unhealthy": total_services - healthy,
            "total_rps": total_rps, "error_rate_pct": error_rate,
            "mtls_coverage_pct": mtls_pct,
            "avg_latency_ms": health.get("avg_latency_ms", 0)}
