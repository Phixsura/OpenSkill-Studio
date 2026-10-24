"""Platform summary — aggregate all developer platform stats."""


def compute_platform_summary(
    *,
    total_developers: int = 0,
    total_apps: int = 0,
    published_apps: int = 0,
    total_installations: int = 0,
    total_executions_24h: int = 0,
    error_rate_24h: float = 0.0,
    webhook_deliveries_24h: int = 0,
    pending_reviews: int = 0,
) -> dict:
    return {
        "developers": total_developers,
        "apps": {"total": total_apps, "published": published_apps, "draft": total_apps - published_apps},
        "installations": total_installations,
        "activity_24h": {
            "executions": total_executions_24h,
            "error_rate": round(error_rate_24h, 2),
            "webhooks": webhook_deliveries_24h,
        },
        "pending_reviews": pending_reviews,
        "health": "healthy" if error_rate_24h < 5 else "degraded" if error_rate_24h < 15 else "critical",
    }
