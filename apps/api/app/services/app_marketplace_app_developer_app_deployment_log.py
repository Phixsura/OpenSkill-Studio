"""Deployment log — track all deployment events with rollback history."""

from datetime import datetime, timezone


def log_deployment(*, app_id: str, version: str, environment: str, deployed_by: str,
                     status: str = "success") -> dict:
    return {"app_id": app_id, "version": version, "environment": environment,
            "deployed_by": deployed_by, "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat()}


def get_deployment_history(*, logs: list[dict], environment: str | None = None,
                              limit: int = 20) -> list[dict]:
    result = logs
    if environment:
        result = [l for l in result if l.get("environment") == environment]
    return sorted(result, key=lambda l: l.get("timestamp", ""), reverse=True)[:limit]


def compute_deployment_frequency(*, logs: list[dict]) -> dict:
    if not logs:
        return {"deploys_per_week": 0, "frequency": "none"}
    count = len(logs)
    freq = "daily" if count > 20 else "weekly" if count > 4 else "monthly" if count > 1 else "rare"
    return {"total_deploys": count, "frequency": freq,
            "success_rate": round(sum(1 for l in logs if l.get("status") == "success") / count * 100, 1)}
