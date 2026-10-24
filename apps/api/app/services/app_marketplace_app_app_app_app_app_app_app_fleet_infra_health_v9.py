"""Fleet Infra Health v9 — track overall infrastructure health score."""
from __future__ import annotations
def fleet_infra_health_v9(components: list[dict]) -> dict:
    healthy_c = [c for c in components if c.get("healthy")]
    degraded = [c for c in components if c.get("degraded")]
    score = round(len(healthy_c) / len(components) * 100, 1) if components else 0
    return {"components": len(components), "healthy": len(healthy_c), "degraded": len(degraded),
            "health_score": score, "all_healthy": len(healthy_c) == len(components)}
