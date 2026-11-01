"""Fleet Deployment Rollout v9 — track progressive rollout percentage."""
from __future__ import annotations
def fleet_deployment_rollout_v9(rollouts: list[dict]) -> dict:
    complete = [r for r in rollouts if r.get("pct") == 100]
    in_progress = [r for r in rollouts if 0 < r.get("pct", 0) < 100]
    paused = [r for r in rollouts if r.get("paused")]
    avg_pct = sum(r.get("pct", 0) for r in rollouts) / len(rollouts) if rollouts else 0
    return {"rollouts": len(rollouts), "complete": len(complete), "in_progress": len(in_progress),
            "paused": len(paused), "avg_pct": round(avg_pct, 1), "healthy": len(paused) == 0}
