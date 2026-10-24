"""Deployment status aggregator — aggregate deployment status across environments."""
from __future__ import annotations
from collections import defaultdict


def aggregate_deploy_status(deployments: list[dict]) -> dict:
    by_env: dict[str, dict] = defaultdict(lambda: {"total": 0, "success": 0, "failed": 0, "in_progress": 0})
    for d in deployments:
        env = d.get("env", "unknown")
        by_env[env]["total"] += 1
        status = d.get("status", "unknown")
        if status == "success":
            by_env[env]["success"] += 1
        elif status == "failed":
            by_env[env]["failed"] += 1
        elif status == "in_progress":
            by_env[env]["in_progress"] += 1
    total = len(deployments)
    all_success = all(d.get("status") == "success" for d in deployments)
    return {"by_env": dict(by_env), "total": total, "all_success": all_success,
            "envs": len(by_env)}


def deploy_velocity(deployments: list[dict], days: int = 7) -> dict:
    per_day = round(len(deployments) / max(days, 1), 1)
    success = sum(1 for d in deployments if d.get("status") == "success")
    success_rate = round(success / max(len(deployments), 1) * 100, 1)
    return {"total_deploys": len(deployments), "per_day": per_day,
            "success_rate": success_rate, "period_days": days}
