"""Deployment pipeline — multi-stage CI/CD pipeline engine."""
from __future__ import annotations
import time


STAGES = ["build", "test", "security_scan", "staging", "approval", "production"]


def create_pipeline(name: str, commit: str, stages: list[str] | None = None) -> dict:
    pipeline_stages = []
    for s in (stages or STAGES):
        pipeline_stages.append({"name": s, "status": "pending", "duration_ms": 0})
    return {"name": name, "commit": commit[:8], "stages": pipeline_stages,
            "current_stage": 0, "status": "pending", "created_at": time.time()}


def advance_pipeline(pipeline: dict, success: bool = True, duration_ms: int = 0) -> dict:
    idx = pipeline["current_stage"]
    if idx >= len(pipeline["stages"]):
        return {"advanced": False, "reason": "pipeline_complete"}
    stage = pipeline["stages"][idx]
    stage["status"] = "passed" if success else "failed"
    stage["duration_ms"] = duration_ms
    if not success:
        pipeline["status"] = "failed"
        return {"advanced": False, "failed_stage": stage["name"]}
    pipeline["current_stage"] += 1
    if pipeline["current_stage"] >= len(pipeline["stages"]):
        pipeline["status"] = "completed"
    else:
        pipeline["status"] = "running"
    return {"advanced": True, "completed_stage": stage["name"],
            "next_stage": pipeline["stages"][pipeline["current_stage"]]["name"] if pipeline["status"] == "running" else None}


def pipeline_summary(pipeline: dict) -> dict:
    passed = sum(1 for s in pipeline["stages"] if s["status"] == "passed")
    total_ms = sum(s["duration_ms"] for s in pipeline["stages"])
    return {"name": pipeline["name"], "status": pipeline["status"],
            "passed": passed, "total": len(pipeline["stages"]),
            "progress_pct": round(passed / len(pipeline["stages"]) * 100),
            "total_duration_ms": total_ms}
