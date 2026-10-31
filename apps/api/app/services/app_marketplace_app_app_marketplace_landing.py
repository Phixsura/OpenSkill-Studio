"""Marketplace landing — homepage content aggregation."""

import html


def build_landing_page(*, featured_apps: list[dict], categories: list[dict],
                         stats: dict, recent_apps: list[dict]) -> dict:
    return {
        "hero": {
            "title": "Discover apps for your workflow",
            "subtitle": "Browse thousands of integrations, tools, and extensions",
        },
        "featured": [{"id": a["id"], "name": html.escape(a.get("name", "")),
                       "icon": a.get("icon", "📦"),
                       "tagline": html.escape(a.get("tagline", ""))} for a in featured_apps[:6]],
        "categories": [{"id": c["id"], "name": html.escape(c.get("name", "")),
                          "icon": c.get("icon", "📂"),
                          "app_count": c.get("app_count", 0)} for c in categories],
        "stats": {
            "total_apps": stats.get("total_apps", 0),
            "total_developers": stats.get("total_developers", 0),
            "total_downloads": stats.get("total_downloads", 0),
        },
        "recent": [{"id": a["id"], "name": html.escape(a.get("name", "")),
                      "icon": a.get("icon", "📦")} for a in recent_apps[:8]],
    }
