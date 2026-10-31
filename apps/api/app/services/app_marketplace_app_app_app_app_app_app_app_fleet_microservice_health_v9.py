"""Fleet Microservice Health v9 — aggregate microservice health dashboard."""
from __future__ import annotations
def fleet_microservice_health_v9(services: list[dict]) -> dict:
    healthy_s = [s for s in services if s.get("healthy")]
    degraded = [s for s in services if s.get("degraded")]
    critical = [s for s in services if s.get("critical")]
    avg_latency = sum(s.get("latency_ms", 0) for s in services) / len(services) if services else 0
    return {"services": len(services), "healthy": len(healthy_s), "degraded": len(degraded),
            "critical": len(critical), "avg_latency_ms": round(avg_latency, 1),
            "all_healthy": len(critical) == 0 and len(degraded) == 0}
