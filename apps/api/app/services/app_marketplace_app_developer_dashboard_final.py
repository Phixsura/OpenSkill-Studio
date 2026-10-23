"""Developer dashboard final — the complete developer dashboard aggregator."""


def build_developer_dashboard(*, developer: dict, apps: list[dict],
                                 analytics: dict, notifications: int) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_revenue = round(sum(a.get("revenue", 0) for a in apps), 2)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    top_app = max(apps, key=lambda a: a.get("installs", 0)) if apps else None
    active_apps = sum(1 for a in apps if a.get("status") == "active")

    return {
        "developer": {
            "name": developer.get("display_name", "Developer"),
            "verified": developer.get("verified", False),
            "plan": developer.get("plan", "free"),
        },
        "overview": {
            "total_apps": len(apps),
            "active_apps": active_apps,
            "total_installs": total_installs,
            "total_revenue": total_revenue,
            "avg_rating": avg_rating,
            "notifications": notifications,
        },
        "top_app": {"name": top_app["name"], "installs": top_app.get("installs", 0)} if top_app else None,
        "analytics": {
            "dau": analytics.get("dau", 0),
            "wau": analytics.get("wau", 0),
            "mau": analytics.get("mau", 0),
            "api_calls_today": analytics.get("api_calls_today", 0),
            "error_rate": analytics.get("error_rate", 0),
        },
        "quick_actions": [
            {"id": "new_app", "label": "Create App", "icon": "➕"},
            {"id": "deploy", "label": "Deploy", "icon": "🚀"},
            {"id": "analytics", "label": "Analytics", "icon": "📊"},
            {"id": "docs", "label": "Docs", "icon": "📚"},
        ],
    }
