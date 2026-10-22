"""Complete developer console — the ULTIMATE aggregator combining every developer tool into one page."""


def build_complete_developer_console(*, developer: dict, apps: list[dict], analytics: dict,
                                        notifications: list[dict], team: list[dict],
                                        onboarding: dict, billing: dict, alerts: list[dict]) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    total_installs = sum(a.get("install_count", 0) for a in apps)
    active_alerts = [a for a in alerts if a.get("triggered")]
    return {
        "page_type": "developer_console",
        "developer": {"name": developer.get("display_name"), "verified": developer.get("verified", False),
                       "plan": billing.get("plan", "free")},
        "dashboard": {
            "apps": {"total": len(apps), "published": len(published), "installs": total_installs},
            "team": {"size": len(team)},
            "alerts": {"active": len(active_alerts), "total": len(alerts)},
            "notifications": {"unread": sum(1 for n in notifications if not n.get("read"))},
        },
        "navigation": [
            {"key": "dashboard", "label": "Dashboard", "icon": "📊"},
            {"key": "apps", "label": f"Apps ({len(apps)})", "icon": "📦"},
            {"key": "analytics", "label": "Analytics", "icon": "📈"},
            {"key": "webhooks", "label": "Webhooks", "icon": "🔗"},
            {"key": "team", "label": f"Team ({len(team)})", "icon": "👥"},
            {"key": "billing", "label": "Billing", "icon": "💳"},
            {"key": "settings", "label": "Settings", "icon": "⚙️"},
            {"key": "docs", "label": "Documentation", "icon": "📚"},
        ],
        "onboarding": onboarding if not onboarding.get("complete") else None,
    }
