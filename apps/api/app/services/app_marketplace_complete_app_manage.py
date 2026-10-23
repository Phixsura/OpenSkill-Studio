"""Complete app management page — the ultimate single-app management view."""


def build_complete_app_manage(*, app: dict, version: dict | None, health: dict,
                                  analytics: dict, webhooks: dict, team: dict,
                                  compliance: dict, install_stats: dict) -> dict:
    return {
        "page_type": "app_management_complete",
        "app": {"id": app["id"], "name": app["name"], "slug": app.get("slug"),
                "status": app.get("status"), "version": version.get("version") if version else None},
        "sidebar": [
            {"key": "overview", "label": "Overview", "icon": "📊", "badge": None},
            {"key": "versions", "label": "Versions", "icon": "📦"},
            {"key": "analytics", "label": "Analytics", "icon": "📈"},
            {"key": "webhooks", "label": f"Webhooks ({webhooks.get('count', 0)})", "icon": "🔗"},
            {"key": "team", "label": f"Team ({team.get('count', 0)})", "icon": "👥"},
            {"key": "settings", "label": "Settings", "icon": "⚙️"},
            {"key": "compliance", "label": "Compliance", "icon": "📋",
             "badge": "⚠️" if not compliance.get("compliant") else None},
        ],
        "overview_cards": [
            {"label": "Installs", "value": install_stats.get("total", 0), "icon": "📥",
             "trend": install_stats.get("trend")},
            {"label": "Health", "value": health.get("grade", "?"), "icon": "💚"},
            {"label": "Rating", "value": analytics.get("avg_rating", 0), "icon": "⭐"},
            {"label": "API Calls", "value": analytics.get("api_calls", 0), "icon": "🌐"},
        ],
    }
