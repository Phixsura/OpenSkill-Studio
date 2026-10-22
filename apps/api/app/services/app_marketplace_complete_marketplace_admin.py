"""Complete marketplace admin — admin dashboard for marketplace operators."""


def build_complete_marketplace_admin(*, platform_stats: dict, pending_reviews: list[dict],
                                        abuse_reports: list[dict], flagged_apps: list[dict],
                                        system_health: dict) -> dict:
    return {
        "page_type": "marketplace_admin",
        "overview": {
            "total_apps": platform_stats.get("total_apps", 0),
            "total_developers": platform_stats.get("total_developers", 0),
            "pending_reviews": len(pending_reviews),
            "open_abuse_reports": len([r for r in abuse_reports if r.get("status") == "open"]),
            "flagged_apps": len(flagged_apps),
        },
        "panels": [
            {"key": "reviews", "title": f"Pending Reviews ({len(pending_reviews)})", "icon": "📝", "priority": True},
            {"key": "abuse", "title": f"Abuse Reports ({len(abuse_reports)})", "icon": "🚨"},
            {"key": "flagged", "title": f"Flagged Apps ({len(flagged_apps)})", "icon": "⚠️"},
            {"key": "health", "title": "System Health", "icon": "💚", "data": system_health},
            {"key": "analytics", "title": "Platform Analytics", "icon": "📊"},
        ],
        "quick_actions": ["approve_app", "reject_app", "suspend_developer", "view_logs"],
    }
