"""Fleet AI Progressive Rollout — track gradual AI feature deployment."""
from __future__ import annotations
def fleet_ai_progressive_rollout(rollouts: list[dict]) -> dict:
    active = [r for r in rollouts if r.get("active", True)]
    current_pct = round(sum(r.get("pct", 0) for r in rollouts) / max(len(rollouts), 1), 1)
    stages_completed = sum(r.get("stages_done", 0) for r in rollouts)
    total_stages = sum(r.get("total_stages", 0) for r in rollouts)
    return {"rollouts": len(rollouts), "active": len(active), "current_pct": current_pct,
            "stages_done": stages_completed, "total_stages": total_stages, "progressing": current_pct < 100}
