"""Developer dashboard layout — compile sidebar, stats, and quick actions."""


def build_dashboard_layout(*, developer: dict, apps: list[dict], notifications_count: int) -> dict:
    sidebar = [
        {"key": "overview", "label": "Overview", "icon": "📊"},
        {"key": "apps", "label": f"Apps ({len(apps)})", "icon": "📦"},
        {"key": "analytics", "label": "Analytics", "icon": "📈"},
        {"key": "webhooks", "label": "Webhooks", "icon": "🔗"},
        {"key": "settings", "label": "Settings", "icon": "⚙️"},
    ]
    quick_stats = {
        "total_apps": len(apps),
        "published": sum(1 for a in apps if a.get("status") == "published"),
        "total_installs": sum(a.get("install_count", 0) for a in apps),
        "pending_reviews": sum(1 for a in apps if a.get("review_status") == "pending"),
    }
    quick_actions = [
        {"label": "Create New App", "action": "create_app", "primary": True},
        {"label": "View Documentation", "action": "open_docs"},
        {"label": "API Keys", "action": "manage_keys"},
    ]
    return {
        "developer_name": developer.get("display_name"),
        "sidebar": sidebar, "quick_stats": quick_stats,
        "quick_actions": quick_actions, "notifications_count": notifications_count,
    }
