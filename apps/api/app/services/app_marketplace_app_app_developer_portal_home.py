"""Developer portal home — main portal landing page content."""

import html
from datetime import datetime, timezone


def build_portal_home(*, user_name: str, apps_count: int = 0, total_installs: int = 0,
                        notifications: int = 0, recent_deploys: list[dict] | None = None,
                        announcements: list[dict] | None = None) -> dict:
    hour = datetime.now(timezone.utc).hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    quick_links = [
        {"label": "Create App", "href": "/apps/new", "icon": "➕"},
        {"label": "API Docs", "href": "/docs/api", "icon": "📋"},
        {"label": "SDK Downloads", "href": "/sdks", "icon": "📦"},
        {"label": "Status Page", "href": "/status", "icon": "🟢"},
        {"label": "Community", "href": "/community", "icon": "💬"},
        {"label": "Changelog", "href": "/changelog", "icon": "📝"},
    ]
    deploys = []
    for d in (recent_deploys or [])[:3]:
        deploys.append({"app": html.escape(d.get("app", "")), "version": d.get("version", ""),
                          "status": d.get("status", "success"), "timestamp": d.get("timestamp", "")})
    anns = [{"title": html.escape(a.get("title", "")), "type": a.get("type", "info")}
            for a in (announcements or [])[:2]]
    return {
        "greeting": f"{greeting}, {html.escape(user_name)}!",
        "stats": {"apps": apps_count, "installs": total_installs, "notifications": notifications},
        "quick_links": quick_links,
        "recent_deploys": deploys,
        "announcements": anns,
    }
