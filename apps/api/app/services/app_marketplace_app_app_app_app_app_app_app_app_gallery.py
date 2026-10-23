"""App gallery — curated collections of marketplace apps."""
from __future__ import annotations
import html


def build_gallery(collections: list[dict]) -> dict:
    result = []
    total_apps = 0
    for col in collections:
        apps = col.get("apps", [])
        total_apps += len(apps)
        result.append({
            "id": col.get("id", ""), "title": html.escape(col.get("title", "")),
            "description": html.escape(col.get("description", "")[:200]),
            "icon": col.get("icon", "📦"), "app_count": len(apps),
            "featured": col.get("featured", False),
            "apps": [{"name": html.escape(a.get("name", "")), "icon": a.get("icon", "📱"),
                       "rating": a.get("rating", 0)} for a in apps[:6]],
        })
    return {"collections": result, "total_collections": len(result),
            "total_apps": total_apps}


def get_featured(collections: list[dict]) -> list[dict]:
    return [c for c in collections if c.get("featured")]
