"""Platform metrics aggregator — compile all platform-level metrics."""


def aggregate_platform_metrics(*, apps: int, developers: int, installations: int,
                                 executions_24h: int, errors_24h: int, webhooks_24h: int,
                                 avg_health: float, active_users_7d: int) -> dict:
    error_rate = round(errors_24h / executions_24h * 100, 2) if executions_24h > 0 else 0
    return {
        "overview": {"apps": apps, "developers": developers, "installations": installations, "active_users_7d": active_users_7d},
        "activity_24h": {"executions": executions_24h, "errors": errors_24h, "error_rate": error_rate, "webhooks": webhooks_24h},
        "health": {"avg_score": round(avg_health, 1), "status": "healthy" if error_rate < 5 else "degraded" if error_rate < 15 else "critical"},
    }
