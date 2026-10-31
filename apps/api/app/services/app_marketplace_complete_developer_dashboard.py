"""Complete developer dashboard — the grand aggregator combining all developer data."""


def build_complete_developer_dashboard(*, developer: dict, apps: list[dict],
                                          notifications: list[dict], analytics: dict,
                                          team: list[dict], onboarding: dict) -> dict:
    unread = sum(1 for n in notifications if not n.get("read"))
    published = [a for a in apps if a.get("status") == "published"]
    total_installs = sum(a.get("install_count", 0) for a in apps)
    return {
        "page_type": "developer_dashboard",
        "developer": {"name": developer.get("display_name"), "verified": developer.get("verified", False)},
        "overview": {
            "total_apps": len(apps), "published_apps": len(published),
            "total_installs": total_installs, "team_size": len(team),
            "unread_notifications": unread,
        },
        "apps": [{"id": a["id"], "name": a["name"], "status": a.get("status"),
                   "installs": a.get("install_count", 0)} for a in apps],
        "analytics_summary": analytics,
        "recent_notifications": notifications[:5],
        "onboarding": onboarding,
        "quick_actions": [
            {"label": "Create App", "action": "create", "icon": "➕"},
            {"label": "View Docs", "action": "docs", "icon": "📚"},
            {"label": "API Keys", "action": "keys", "icon": "🔑"},
        ],
    }
