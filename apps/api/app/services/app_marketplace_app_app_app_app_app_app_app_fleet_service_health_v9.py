"""Fleet Service Health v9 — aggregate service health across all tiers."""
from __future__ import annotations
def fleet_service_health_v9(services: list[dict]) -> dict:
    healthy_svc = [s for s in services if s.get("healthy")]
    degraded = [s for s in services if s.get("degraded")]
    down = [s for s in services if s.get("down")]
    uptime = round(len(healthy_svc) / len(services) * 100, 2) if services else 0
    return {"services": len(services), "healthy": len(healthy_svc), "degraded": len(degraded),
            "down": len(down), "uptime_pct": uptime, "all_healthy": len(down) == 0 and len(degraded) == 0}
