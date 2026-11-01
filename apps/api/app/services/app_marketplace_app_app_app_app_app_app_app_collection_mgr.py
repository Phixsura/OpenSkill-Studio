"""App collection manager — curated collections of marketplace apps."""
from __future__ import annotations
import html


def create_collection(*, title: str, description: str, curator: str,
                        app_ids: list[str], featured: bool = False) -> dict:
    return {
        "title": html.escape(title), "description": html.escape(description[:300]),
        "curator": curator, "app_ids": app_ids, "app_count": len(app_ids),
        "featured": featured,
    }


def build_collection_page(collections: list[dict]) -> dict:
    featured = [c for c in collections if c.get("featured")]
    total_apps = sum(c.get("app_count", 0) for c in collections)
    return {"collections": collections, "total_collections": len(collections),
            "featured_count": len(featured), "total_apps": total_apps}


def add_to_collection(collection: dict, app_id: str) -> dict:
    if app_id in collection.get("app_ids", []):
        return {"error": "App already in collection"}
    collection.setdefault("app_ids", []).append(app_id)
    collection["app_count"] = len(collection["app_ids"])
    return {"added": True, "app_count": collection["app_count"]}
