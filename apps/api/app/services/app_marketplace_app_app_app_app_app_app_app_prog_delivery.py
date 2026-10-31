"""Progressive delivery controller — manage staged rollouts."""
from __future__ import annotations


def create_progressive_rollout(deployment: str, stages: list[dict]) -> dict:
    items = []
    for i, s in enumerate(stages):
        items.append({"stage": i + 1, "name": s.get("name", f"Stage {i+1}"),
                       "traffic_pct": s.get("traffic_pct", 0),
                       "duration_min": s.get("duration_min", 10),
                       "status": "pending", "metrics_ok": None})
    return {"deployment": deployment, "stages": items, "current_stage": 0,
            "total_stages": len(items), "status": "in_progress"}


def advance_stage(rollout: dict, metrics_ok: bool) -> dict:
    idx = rollout["current_stage"]
    if idx >= rollout["total_stages"]:
        return {"advanced": False, "reason": "complete"}
    stage = rollout["stages"][idx]
    stage["metrics_ok"] = metrics_ok
    if not metrics_ok:
        stage["status"] = "failed"
        rollout["status"] = "rolled_back"
        return {"advanced": False, "action": "rollback", "failed_stage": stage["name"]}
    stage["status"] = "completed"
    rollout["current_stage"] += 1
    if rollout["current_stage"] >= rollout["total_stages"]:
        rollout["status"] = "complete"
    return {"advanced": True, "stage": stage["name"],
            "next_stage": rollout["current_stage"] + 1 if rollout["status"] != "complete" else None}
