"""Fleet progressive delivery — track gradual rollout progress."""
from __future__ import annotations
def fleet_progressive_delivery(rollouts: list[dict]) -> dict:
    in_progress = [r for r in rollouts if r.get("phase") == "progressing"]
    completed = [r for r in rollouts if r.get("phase") == "completed"]
    paused = [r for r in rollouts if r.get("phase") == "paused"]
    return {"total": len(rollouts), "in_progress": len(in_progress),
            "completed": len(completed), "paused": len(paused)}
