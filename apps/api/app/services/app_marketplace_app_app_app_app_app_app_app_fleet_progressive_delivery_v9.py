"""Fleet Progressive Delivery v9 — track progressive rollout strategies."""
from __future__ import annotations
def fleet_progressive_delivery_v9(rollouts: list[dict]) -> dict:
    in_progress = [r for r in rollouts if r.get("phase") in ("canary", "analysis", "pause")]
    completed = [r for r in rollouts if r.get("phase") == "completed"]
    aborted = [r for r in rollouts if r.get("phase") == "aborted"]
    return {"rollouts": len(rollouts), "in_progress": len(in_progress), "completed": len(completed),
            "aborted": len(aborted), "healthy": len(aborted) == 0}
