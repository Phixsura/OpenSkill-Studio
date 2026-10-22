"""Complete app management page — the FINAL master aggregator for managing an installed app."""


def build_complete_app_management_page(*, installation: dict, app: dict, config: dict,
                                          health: dict, usage: dict, scheduled_tasks: list[dict],
                                          feature_flags: list[dict], logs_summary: dict) -> dict:
    return {
        "page_type": "app_management",
        "installation": {"id": installation["id"], "status": installation.get("status")},
        "app": {"id": app["id"], "name": app["name"], "version": app.get("current_version")},
        "tabs": [
            {"key": "overview", "title": "Overview", "icon": "📊"},
            {"key": "config", "title": "Configuration", "icon": "⚙️"},
            {"key": "health", "title": "Health", "icon": "💚", "data": health},
            {"key": "usage", "title": "Usage", "icon": "📈", "data": usage},
            {"key": "tasks", "title": f"Tasks ({len(scheduled_tasks)})", "icon": "⏰"},
            {"key": "flags", "title": f"Flags ({len(feature_flags)})", "icon": "🚩"},
            {"key": "logs", "title": "Logs", "icon": "📋", "data": logs_summary},
        ],
        "quick_actions": ["update", "rollback", "uninstall", "configure"],
    }
