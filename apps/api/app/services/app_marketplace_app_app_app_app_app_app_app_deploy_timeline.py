"""Deployment timeline — visualize deployment history over time."""
from __future__ import annotations


def build_deploy_timeline(deploys: list[dict]) -> dict:
    by_env: dict[str, int] = {}
    by_status: dict[str, int] = {}
    total_duration = 0
    for d in deploys:
        env = d.get("environment", "production")
        status = d.get("status", "success")
        by_env[env] = by_env.get(env, 0) + 1
        by_status[status] = by_status.get(status, 0) + 1
        total_duration += d.get("duration_sec", 0)
    success_rate = round(by_status.get("success", 0) / max(len(deploys), 1) * 100)
    avg_duration = round(total_duration / max(len(deploys), 1))
    return {"deploys": deploys, "total": len(deploys), "by_environment": by_env,
            "by_status": by_status, "success_rate": success_rate,
            "avg_duration_sec": avg_duration}
