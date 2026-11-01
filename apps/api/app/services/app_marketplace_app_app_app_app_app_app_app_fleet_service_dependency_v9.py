"""Fleet Service Dependency v9 — track inter-service dependency health."""
from __future__ import annotations
def fleet_service_dependency_v9(deps: list[dict]) -> dict:
    healthy_d = [d for d in deps if d.get("healthy")]
    circular = [d for d in deps if d.get("circular")]
    avg_latency = sum(d.get("latency_ms", 0) for d in deps) / len(deps) if deps else 0
    return {"dependencies": len(deps), "healthy": len(healthy_d), "circular": len(circular),
            "avg_latency_ms": round(avg_latency, 1), "all_healthy": len(healthy_d) == len(deps)}
