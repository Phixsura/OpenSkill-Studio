"""Fleet API Dependency Check v9 — track API dependency health checks."""
from __future__ import annotations
def fleet_api_dependency_check_v9(deps: list[dict]) -> dict:
    healthy_d = [d for d in deps if d.get("healthy")]
    degraded = [d for d in deps if d.get("degraded")]
    down = [d for d in deps if d.get("down")]
    return {"dependencies": len(deps), "healthy": len(healthy_d), "degraded": len(degraded),
            "down": len(down), "all_healthy": len(healthy_d) == len(deps)}
