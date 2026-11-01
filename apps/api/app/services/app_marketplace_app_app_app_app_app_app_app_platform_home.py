"""Platform home — the ultimate OpenSkill platform home page."""

import html
from datetime import datetime, timezone


def build_platform_home(*, user: dict | None = None, featured_apps: list[dict],
                           trending_apps: list[dict], categories: list[dict],
                           platform_stats: dict) -> dict:
    user_info = None
    if user:
        user_info = {"name": html.escape(user.get("name", "")),
                      "plan": user.get("plan", "free"),
                      "app_count": user.get("app_count", 0)}
    featured = [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                  "icon": a.get("icon", "📦"), "tagline": html.escape(a.get("tagline", "")),
                  "rating": a.get("rating", 0)} for a in featured_apps[:6]]
    trending = [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                  "icon": a.get("icon", "📦"), "growth": a.get("growth_pct", 0)}
                 for a in trending_apps[:6]]
    cats = [{"id": c.get("id"), "name": html.escape(c.get("name", "")),
              "icon": c.get("icon", "📂"), "count": c.get("count", 0)}
             for c in categories[:12]]
    return {
        "user": user_info,
        "hero": {
            "title": "OpenSkill Marketplace",
            "subtitle": "Discover, install, and build apps for your workflow",
        },
        "stats": {
            "apps": platform_stats.get("apps", 0),
            "developers": platform_stats.get("developers", 0),
            "downloads": platform_stats.get("downloads", 0),
            "uptime": platform_stats.get("uptime_pct", 99.99),
        },
        "featured": featured,
        "trending": trending,
        "categories": cats,
        "sections": ["hero", "stats", "featured", "trending", "categories"],
    }
