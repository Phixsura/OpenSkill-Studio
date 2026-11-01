"""Fleet Deployment Velocity v9 — track deployment speed and frequency."""
from __future__ import annotations
def fleet_deployment_velocity_v9(teams: list[dict]) -> dict:
    deploys_week = sum(t.get("deploys_per_week", 0) for t in teams)
    avg_time = sum(t.get("avg_deploy_min", 0) for t in teams) / len(teams) if teams else 0
    rollback_rate = sum(t.get("rollback_rate", 0) for t in teams) / len(teams) if teams else 0
    return {"teams": len(teams), "deploys_per_week": deploys_week,
            "avg_deploy_min": round(avg_time, 1), "rollback_rate_pct": round(rollback_rate, 2),
            "healthy": rollback_rate < 5}
