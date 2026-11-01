"""Developer homepage — the complete landing page for the developer portal."""


def build_developer_homepage(*, developer: dict, apps: list[dict], stats: dict,
                                 notifications: list[dict], onboarding: dict,
                                 recent_activity: list[dict], announcements: list[dict]) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    unread = sum(1 for n in notifications if not n.get("read"))
    return {
        "page_type": "developer_homepage",
        "welcome": {"name": developer.get("display_name"), "plan": developer.get("plan", "free"),
                      "verified": developer.get("verified", False)},
        "stats_cards": [
            {"key": "apps", "label": "Published Apps", "value": len(published), "icon": "📦", "url": "/developer/apps"},
            {"key": "installs", "label": "Total Installs", "value": stats.get("total_installs", 0), "icon": "📥"},
            {"key": "rating", "label": "Avg Rating", "value": stats.get("avg_rating", 0), "icon": "⭐"},
            {"key": "revenue", "label": "This Month", "value": stats.get("mrr", "$0"), "icon": "💰"},
        ],
        "sections": [
            {"key": "activity", "title": "Recent Activity", "items": recent_activity[:5]},
            {"key": "notifications", "title": f"Notifications ({unread} new)", "items": notifications[:5]},
            {"key": "announcements", "title": "Announcements", "items": announcements[:3]},
        ],
        "onboarding": onboarding if not onboarding.get("complete") else None,
        "quick_actions": [
            {"label": "Create App", "url": "/developer/apps/new", "icon": "➕", "primary": True},
            {"label": "View Analytics", "url": "/developer/analytics", "icon": "📊"},
            {"label": "API Docs", "url": "/docs/api", "icon": "📚"},
            {"label": "Community", "url": "/community", "icon": "💬"},
        ],
    }
