"""Marketplace admin v2 — enhanced admin tools with moderation queue and bulk actions."""


def build_admin_dashboard_v2(*, stats: dict, moderation_queue: list[dict],
                                flagged_content: list[dict], system_alerts: list[dict]) -> dict:
    urgent = [a for a in system_alerts if a.get("severity") == "critical"]
    pending = [m for m in moderation_queue if m.get("status") == "pending"]
    return {
        "page_type": "admin_v2",
        "overview": {
            "pending_moderation": len(pending),
            "flagged_content": len(flagged_content),
            "critical_alerts": len(urgent),
            "total_apps": stats.get("total_apps", 0),
        },
        "panels": [
            {"key": "moderation", "title": f"Moderation Queue ({len(pending)})", "priority": len(pending) > 0},
            {"key": "flags", "title": f"Flagged Content ({len(flagged_content)})"},
            {"key": "alerts", "title": f"System Alerts ({len(urgent)} critical)"},
            {"key": "stats", "title": "Platform Stats"},
        ],
        "needs_attention": len(pending) > 0 or len(urgent) > 0,
    }
