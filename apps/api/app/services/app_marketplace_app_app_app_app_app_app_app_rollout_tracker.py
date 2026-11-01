"""Deployment rollout tracker — monitor progressive deployment rollouts."""
from __future__ import annotations
import time


def create_rollout(deployment_id: str, target_pct: float = 100.0,
                    steps: list[float] | None = None) -> dict:
    step_list = steps or [5, 25, 50, 75, 100]
    return {"deployment_id": deployment_id, "current_pct": 0, "target_pct": target_pct,
            "steps": step_list, "current_step": 0, "status": "in_progress",
            "started_at": time.time(), "paused": False}


def advance_rollout(rollout: dict) -> dict:
    if rollout["paused"]:
        return {"advanced": False, "reason": "paused"}
    if rollout["current_step"] >= len(rollout["steps"]):
        return {"advanced": False, "reason": "complete"}
    rollout["current_pct"] = rollout["steps"][rollout["current_step"]]
    rollout["current_step"] += 1
    if rollout["current_pct"] >= rollout["target_pct"]:
        rollout["status"] = "complete"
    return {"advanced": True, "current_pct": rollout["current_pct"],
            "status": rollout["status"],
            "remaining_steps": len(rollout["steps"]) - rollout["current_step"]}


def pause_rollout(rollout: dict) -> dict:
    rollout["paused"] = True
    rollout["status"] = "paused"
    return {"paused": True, "at_pct": rollout["current_pct"]}


def rollout_summary(rollouts: list[dict]) -> dict:
    in_progress = sum(1 for r in rollouts if r["status"] == "in_progress")
    complete = sum(1 for r in rollouts if r["status"] == "complete")
    paused = sum(1 for r in rollouts if r["status"] == "paused")
    return {"total": len(rollouts), "in_progress": in_progress,
            "complete": complete, "paused": paused}
