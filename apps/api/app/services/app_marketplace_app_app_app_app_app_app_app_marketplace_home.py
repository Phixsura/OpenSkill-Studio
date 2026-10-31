"""Marketplace home builder — assemble the marketplace landing page data."""
from __future__ import annotations
import html


def build_marketplace_home(*, featured_apps: list[dict], categories: list[dict],
                              trending: list[dict], new_apps: list[dict],
                              total_apps: int, total_developers: int) -> dict:
    return {
        "hero": {
            "title": "OpenSkill Marketplace",
            "subtitle": f"Discover {total_apps:,} apps from {total_developers:,} developers",
            "cta": "Explore Apps",
        },
        "featured": [_format_app(a) for a in featured_apps[:6]],
        "categories": [{"id": c.get("id", ""), "label": html.escape(c.get("label", "")),
                          "icon": c.get("icon", "📦"), "count": c.get("count", 0)}
                         for c in categories],
        "trending": [_format_app(a) for a in trending[:8]],
        "new_apps": [_format_app(a) for a in new_apps[:8]],
        "stats": {"total_apps": total_apps, "total_developers": total_developers,
                   "apps_display": f"{total_apps:,}", "devs_display": f"{total_developers:,}"},
    }


def _format_app(app: dict) -> dict:
    return {"name": html.escape(app.get("name", "")), "icon": app.get("icon", "📱"),
            "rating": app.get("rating", 0), "installs": app.get("installs", 0),
            "category": app.get("category", ""), "developer": app.get("developer", "")}
