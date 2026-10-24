"""Deployment log — track all deployment history with status and metadata."""

import secrets
from datetime import datetime


def create_deployment_entry(*, app_id: str, version: str, environment: str,
                               deployed_by: str, strategy: str = "rolling") -> dict:
    return {
        "deployment_id": f"deploy_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "version": version,
        "environment": environment,
        "deployed_by": deployed_by,
        "strategy": strategy,
        "status": "in_progress",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "duration_sec": None,
    }


def get_deployment_stats(*, deployments: list[dict]) -> dict:
    total = len(deployments)
    successful = sum(1 for d in deployments if d.get("status") == "success")
    failed = sum(1 for d in deployments if d.get("status") == "failed")
    durations = [d.get("duration_sec", 0) for d in deployments if d.get("duration_sec")]
    avg_duration = round(sum(durations) / max(len(durations), 1), 1)
    by_env: dict[str, int] = {}
    for d in deployments:
        env = d.get("environment", "unknown")
        by_env[env] = by_env.get(env, 0) + 1
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": round(successful / max(total, 1) * 100, 1),
        "avg_duration_sec": avg_duration,
        "by_environment": by_env,
    }
