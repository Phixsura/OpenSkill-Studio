"""Deployment pipeline builder — configure multi-stage deployment pipelines."""
from __future__ import annotations


def create_pipeline(*, name: str, stages: list[dict]) -> dict:
    built = []
    for i, s in enumerate(stages):
        built.append({
            "index": i, "name": s["name"], "type": s.get("type", "deploy"),
            "environment": s.get("environment", "staging"),
            "approval_required": s.get("approval_required", False),
            "auto_rollback": s.get("auto_rollback", True),
            "timeout_min": s.get("timeout_min", 30),
            "status": "pending",
        })
    return {"name": name, "stages": built, "total_stages": len(built),
            "has_approval_gates": any(s["approval_required"] for s in built)}


def execute_pipeline(pipeline: dict) -> dict:
    results = []
    for stage in pipeline["stages"]:
        if stage["approval_required"] and stage["status"] == "pending":
            stage["status"] = "awaiting_approval"
            results.append({"stage": stage["name"], "status": "awaiting_approval"})
            break
        stage["status"] = "completed"
        results.append({"stage": stage["name"], "status": "completed"})
    completed = sum(1 for s in pipeline["stages"] if s["status"] == "completed")
    return {"results": results, "completed": completed,
            "total": pipeline["total_stages"],
            "progress_pct": round(completed / pipeline["total_stages"] * 100),
            "blocked": any(s["status"] == "awaiting_approval" for s in pipeline["stages"])}
