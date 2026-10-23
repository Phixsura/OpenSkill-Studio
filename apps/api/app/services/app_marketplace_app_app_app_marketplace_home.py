"""App marketplace home — complete marketplace homepage builder."""

import html


def build_marketplace_home(*, featured: list[dict], trending: list[dict],
                              categories: list[dict], new_apps: list[dict],
                              total_apps: int, total_developers: int) -> dict:
    return {
        "hero": {
            "title": "OpenSkill Marketplace",
            "subtitle": "Discover, install, and build apps for your workflow",
            "stats": {
                "total_apps": total_apps, "total_developers": total_developers,
                "apps_display": f"{total_apps:,}", "devs_display": f"{total_developers:,}",
            },
        },
        "featured": [{"id": a["id"], "name": html.escape(a.get("name", "")),
                       "icon": a.get("icon", "📦"), "tagline": html.escape(a.get("tagline", "")),
                       "rating": a.get("rating", 0)} for a in featured[:6]],
        "trending": [{"id": a["id"], "name": html.escape(a.get("name", "")),
                       "icon": a.get("icon", "📦"),
                       "growth_pct": a.get("growth_pct", 0)} for a in trending[:6]],
        "categories": [{"id": c["id"], "name": html.escape(c.get("name", "")),
                          "icon": c.get("icon", "📂"),
                          "count": c.get("count", 0)} for c in categories],
        "new_apps": [{"id": a["id"], "name": html.escape(a.get("name", "")),
                       "icon": a.get("icon", "🆕")} for a in new_apps[:8]],
        "section_count": 4,  # featured, trending, categories, new
    }
