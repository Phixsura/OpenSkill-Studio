"""Deployment pipeline — manage staged rollout deployments."""

import secrets
from datetime import datetime


def create_deployment(*, app_id: str, version: str, strategy: str = "rolling",
                       rollout_pct: int = 10) -> dict:
    valid_strategies = {"rolling", "blue_green", "canary", "all_at_once"}
    if strategy not in valid_strategies:
        return {"error": f"Invalid strategy. Valid: {', '.join(sorted(valid_strategies))}"}
    if not 1 <= rollout_pct <= 100:
        return {"error": "Rollout percentage must be 1-100"}
    return {
        "deployment_id": f"dep_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "version": version,
        "strategy": strategy,
        "rollout_pct": rollout_pct,
        "status": "pending",
        "stages": [
            {"name": "build", "status": "pending"},
            {"name": "test", "status": "pending"},
            {"name": "staging", "status": "pending"},
            {"name": "production", "status": "pending"},
        ],
        "created_at": datetime.utcnow().isoformat(),
    }


def advance_deployment(*, deployment: dict, stage_name: str, success: bool) -> dict:
    stages = deployment.get("stages", [])
    for s in stages:
        if s["name"] == stage_name:
            s["status"] = "success" if success else "failed"
            break
    all_done = all(s["status"] == "success" for s in stages)
    any_failed = any(s["status"] == "failed" for s in stages)
    return {
        "stages": stages,
        "status": "completed" if all_done else "failed" if any_failed else "in_progress",
        "completed": all_done,
    }
