"""Fleet API Dependency Health v9 — track downstream dependency health."""
from __future__ import annotations
def fleet_api_dependency_health_v9(deps: list[dict]) -> dict:
    healthy_d = [d for d in deps if d.get("healthy")]
    degraded = [d for d in deps if d.get("degraded")]
    down = [d for d in deps if d.get("down")]
    avg_latency = sum(d.get("latency_ms", 0) for d in deps) / len(deps) if deps else 0
    return {"dependencies": len(deps), "healthy": len(healthy_d), "degraded": len(degraded),
            "down": len(down), "avg_latency_ms": round(avg_latency, 1), "all_healthy": len(down) == 0 and len(degraded) == 0}
