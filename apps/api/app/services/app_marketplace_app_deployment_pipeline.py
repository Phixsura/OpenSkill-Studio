"""Deployment pipeline — manage staged rollout for app versions."""

from datetime import datetime, timezone


def create_pipeline(*, app_id: str, version_id: str, stages: list[str] | None = None) -> dict:
    default_stages = ["validation", "security_scan", "staging", "canary", "production"]
    pipeline_stages = []
    for s in (stages or default_stages):
        pipeline_stages.append({"name": s, "status": "pending", "started_at": None, "completed_at": None})
    return {"app_id": app_id, "version_id": version_id, "stages": pipeline_stages,
            "current_stage": 0, "status": "created"}


def advance_stage(*, pipeline: dict) -> dict:
    idx = pipeline["current_stage"]
    stages = list(pipeline["stages"])
    if idx >= len(stages):
        return {**pipeline, "status": "completed"}
    now = datetime.now(timezone.utc).isoformat()
    stages[idx] = {**stages[idx], "status": "completed", "completed_at": now}
    new_idx = idx + 1
    if new_idx < len(stages):
        stages[new_idx] = {**stages[new_idx], "status": "running", "started_at": now}
    status = "completed" if new_idx >= len(stages) else "running"
    return {**pipeline, "stages": stages, "current_stage": new_idx, "status": status}


def get_pipeline_progress(*, pipeline: dict) -> dict:
    total = len(pipeline["stages"])
    completed = sum(1 for s in pipeline["stages"] if s["status"] == "completed")
    return {"completed": completed, "total": total, "pct": round(completed / max(total, 1) * 100)}
