"""App analytics builder — compile analytics page data for a single app."""


def build_app_analytics(*, app: dict, install_trend: list[dict], execution_stats: dict,
                          webhook_stats: dict, health_trend: dict) -> dict:
    return {
        "app": {"name": app.get("name"), "slug": app.get("slug")},
        "install_trend": install_trend,
        "execution_stats": execution_stats,
        "webhook_stats": webhook_stats,
        "health_trend": health_trend,
        "sections": ["installs", "executions", "webhooks", "health"],
    }
