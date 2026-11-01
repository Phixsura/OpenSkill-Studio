"""Fleet Argo Rollouts — track progressive delivery rollouts."""
from __future__ import annotations
def fleet_argo_rollouts(rollouts: list[dict]) -> dict:
    healthy = [r for r in rollouts if r.get("phase") == "Healthy"]
    paused = [r for r in rollouts if r.get("phase") == "Paused"]
    degraded = [r for r in rollouts if r.get("phase") == "Degraded"]
    return {"total": len(rollouts), "healthy": len(healthy), "paused": len(paused),
            "degraded": len(degraded), "all_healthy": len(healthy) == len(rollouts)}
