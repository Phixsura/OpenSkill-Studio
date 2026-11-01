"""Developer portal home — landing page for the developer portal."""


def build_portal_home(*, developer: dict, apps: list[dict], notifications: int) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_revenue = round(sum(a.get("revenue", 0) for a in apps), 2)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1)
    recent_apps = sorted(apps, key=lambda a: a.get("updated_at", ""), reverse=True)[:3]
    quick_links = [
        {"label": "Create New App", "icon": "➕", "url": "/apps/new"},
        {"label": "Documentation", "icon": "📚", "url": "/docs"},
        {"label": "API Reference", "icon": "🔌", "url": "/docs/api"},
        {"label": "Analytics", "icon": "📊", "url": "/analytics"},
        {"label": "Settings", "icon": "⚙️", "url": "/settings"},
        {"label": "Support", "icon": "💬", "url": "/support"},
    ]
    return {
        "greeting": f"Welcome back, {developer.get('display_name', 'Developer')}!",
        "stats": {"apps": len(apps), "installs": total_installs,
                   "revenue": total_revenue, "avg_rating": avg_rating},
        "recent_apps": [{"id": a["id"], "name": a["name"],
                          "installs": a.get("installs", 0)} for a in recent_apps],
        "notifications": notifications,
        "quick_links": quick_links,
    }
