"""Developer dashboard v2 — next-gen dashboard with real-time widgets."""


def build_dashboard_v2(*, developer: dict, apps: list[dict], inbox: dict,
                         health: dict, revenue: dict | None = None) -> dict:
    published = [a for a in apps if a.get("status") == "published"]
    return {
        "page_type": "dashboard_v2",
        "header": {"name": developer.get("display_name"), "tier": developer.get("tier", "free"),
                    "unread_messages": inbox.get("unread", 0)},
        "widgets": [
            {"key": "apps", "title": "My Apps", "value": len(apps), "subtitle": f"{len(published)} published"},
            {"key": "health", "title": "Platform Health", "value": health.get("status", "healthy")},
            {"key": "installs", "title": "Total Installs", "value": sum(a.get("install_count", 0) for a in apps)},
        ] + ([{"key": "revenue", "title": "MRR", "value": revenue.get("mrr", "$0")}] if revenue else []),
        "quick_actions": ["create_app", "view_analytics", "open_docs", "manage_team"],
    }
