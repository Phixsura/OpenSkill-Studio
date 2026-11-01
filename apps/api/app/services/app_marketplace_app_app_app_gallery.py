"""App gallery — curated app collection with categories."""

import html


def build_gallery(*, collections: list[dict]) -> dict:
    items = []
    total_apps = 0
    for c in collections:
        apps = c.get("apps", [])
        total_apps += len(apps)
        items.append({
            "title": html.escape(c.get("title", "")),
            "description": html.escape(c.get("description", "")),
            "icon": c.get("icon", "📦"),
            "apps": [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                       "icon": a.get("icon", "📦")} for a in apps],
            "app_count": len(apps),
        })
    return {"collections": items, "total_collections": len(items),
            "total_apps": total_apps}
