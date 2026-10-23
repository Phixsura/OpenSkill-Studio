"""App category page — category browsing with app listings."""

import html


def build_category_page(*, category: dict, apps: list[dict],
                          sort_by: str = "popular") -> dict:
    sorted_apps = list(apps)
    if sort_by == "popular":
        sorted_apps.sort(key=lambda a: a.get("downloads", 0), reverse=True)
    elif sort_by == "rating":
        sorted_apps.sort(key=lambda a: a.get("rating", 0), reverse=True)
    elif sort_by == "newest":
        sorted_apps.sort(key=lambda a: a.get("created_at", ""), reverse=True)
    items = [{
        "id": a.get("id", ""), "name": html.escape(a.get("name", "")),
        "icon": a.get("icon", "📦"), "tagline": html.escape(a.get("tagline", "")),
        "rating": a.get("rating", 0), "downloads": a.get("downloads", 0),
    } for a in sorted_apps]
    return {
        "category": {"id": category["id"], "name": html.escape(category.get("name", "")),
                       "icon": category.get("icon", "📂"),
                       "description": html.escape(category.get("description", ""))},
        "apps": items, "total": len(items), "sort_by": sort_by,
    }
