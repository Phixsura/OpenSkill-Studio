"""API usage dashboard — compile dashboard data for developer portal."""


def build_dashboard_data(*, apps: list[dict], total_api_calls: int = 0, total_executions: int = 0,
                         total_webhooks: int = 0, health_scores: list[int] | None = None) -> dict:
    scores = health_scores or []
    avg_health = round(sum(scores) / len(scores), 1) if scores else 100.0
    published = sum(1 for a in apps if a.get("status") == "published")
    return {
        "summary": {
            "total_apps": len(apps), "published": published, "draft": len(apps) - published,
            "api_calls": total_api_calls, "executions": total_executions, "webhooks": total_webhooks,
            "avg_health": avg_health,
        },
        "apps": [{"id": a.get("id"), "name": a.get("name"), "status": a.get("status")} for a in apps],
    }
