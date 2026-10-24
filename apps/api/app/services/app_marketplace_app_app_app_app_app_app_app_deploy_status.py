"""Deployment status tracker — real-time deployment progress."""
from __future__ import annotations
import time


def create_deployment(deploy_id: str, version: str, environment: str,
                       steps: list[str]) -> dict:
    return {"deploy_id": deploy_id, "version": version, "environment": environment,
            "steps": [{"name": s, "status": "pending", "duration_ms": 0} for s in steps],
            "current_step": 0, "status": "in_progress", "started_at": time.time()}


def update_step(deployment: dict, step_name: str, status: str, duration_ms: int = 0) -> dict:
    for s in deployment["steps"]:
        if s["name"] == step_name:
            s["status"] = status
            s["duration_ms"] = duration_ms
            break
    completed = sum(1 for s in deployment["steps"] if s["status"] == "completed")
    failed = any(s["status"] == "failed" for s in deployment["steps"])
    if failed:
        deployment["status"] = "failed"
    elif completed == len(deployment["steps"]):
        deployment["status"] = "completed"
    total_ms = sum(s["duration_ms"] for s in deployment["steps"])
    return {"deploy_id": deployment["deploy_id"], "status": deployment["status"],
            "progress": round(completed / len(deployment["steps"]) * 100),
            "total_duration_ms": total_ms}


def deployment_summary(deployments: list[dict]) -> dict:
    by_status: dict[str, int] = {}
    for d in deployments:
        by_status[d["status"]] = by_status.get(d["status"], 0) + 1
    return {"total": len(deployments), "by_status": by_status,
            "success_rate": round(by_status.get("completed", 0) / max(len(deployments), 1) * 100)}
