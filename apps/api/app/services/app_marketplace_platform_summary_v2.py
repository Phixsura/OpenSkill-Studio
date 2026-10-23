"""Platform summary v2 — the comprehensive overview of the entire developer ecosystem."""


def build_platform_summary_v2(*, stats: dict, health: dict, growth: dict,
                                  top_apps: list[dict], recent_activity: list[dict]) -> dict:
    return {
        "page_type": "platform_summary_v2",
        "headline": {
            "total_apps": stats.get("apps", 0),
            "total_developers": stats.get("developers", 0),
            "total_installs": stats.get("installs", 0),
            "api_calls_today": stats.get("api_calls_today", 0),
        },
        "health": health,
        "growth": {
            "apps_this_month": growth.get("apps_this_month", 0),
            "developers_this_month": growth.get("developers_this_month", 0),
            "installs_this_month": growth.get("installs_this_month", 0),
        },
        "top_apps": top_apps[:5],
        "recent_activity": recent_activity[:10],
        "links": {
            "marketplace": "/marketplace", "docs": "/docs",
            "status": "/status", "blog": "/blog",
        },
    }
