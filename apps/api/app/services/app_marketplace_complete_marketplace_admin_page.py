"""Complete marketplace admin page — admin dashboard for platform operators."""


def build_complete_admin_page(*, platform_stats: dict, pending_reviews: list[dict],
                                   abuse_reports: list[dict], flagged_apps: list[dict],
                                   system_health: dict, recent_actions: list[dict]) -> dict:
    open_reports = [r for r in abuse_reports if r.get("status") == "open"]
    return {
        "page_type": "marketplace_admin",
        "overview": {
            "total_apps": platform_stats.get("total_apps", 0),
            "total_developers": platform_stats.get("total_developers", 0),
            "pending_reviews": len(pending_reviews),
            "open_reports": len(open_reports),
            "flagged_apps": len(flagged_apps),
            "system_health": system_health.get("status", "unknown"),
        },
        "priority_queue": [
            {"key": "reviews", "title": f"Pending Reviews ({len(pending_reviews)})", "icon": "📝",
             "priority": len(pending_reviews) > 0, "items": pending_reviews[:10]},
            {"key": "abuse", "title": f"Abuse Reports ({len(open_reports)})", "icon": "🚨",
             "priority": len(open_reports) > 0, "items": open_reports[:10]},
            {"key": "flagged", "title": f"Flagged Apps ({len(flagged_apps)})", "icon": "⚠️",
             "priority": len(flagged_apps) > 0, "items": flagged_apps[:10]},
        ],
        "recent_actions": recent_actions[:20],
        "quick_actions": ["approve_all_safe", "bulk_review", "system_check", "generate_report"],
    }
