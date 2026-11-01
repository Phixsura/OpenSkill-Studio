"""Platform dashboard summary — executive overview of the entire platform."""


def build_platform_summary(*, stats: dict) -> dict:
    return {
        "page_type": "platform_dashboard",
        "overview": {
            "total_apps": stats.get("total_apps", 0),
            "total_developers": stats.get("total_developers", 0),
            "total_users": stats.get("total_users", 0),
            "total_installs": stats.get("total_installs", 0),
        },
        "revenue": {
            "mrr": stats.get("mrr", 0),
            "arr": round(stats.get("mrr", 0) * 12, 2),
            "growth_pct": stats.get("revenue_growth_pct", 0),
        },
        "health": {
            "uptime_pct": stats.get("uptime_pct", 99.99),
            "avg_latency_ms": stats.get("avg_latency_ms", 45),
            "error_rate": stats.get("error_rate", 0.01),
            "active_incidents": stats.get("active_incidents", 0),
        },
        "engagement": {
            "dau": stats.get("dau", 0),
            "wau": stats.get("wau", 0),
            "mau": stats.get("mau", 0),
            "retention_30d": stats.get("retention_30d", 0),
        },
        "status": "operational" if stats.get("active_incidents", 0) == 0 else "degraded",
    }
