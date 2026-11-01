"""App collection — curated app collection management."""

import html
import secrets
from datetime import datetime, timezone


def create_collection(*, title: str, description: str, curator: str,
                        apps: list[str]) -> dict:
    return {
        "id": f"col_{secrets.token_hex(6)}",
        "title": html.escape(title),
        "description": html.escape(description),
        "curator": html.escape(curator),
        "app_ids": apps,
        "app_count": len(apps),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "featured": False,
    }


def build_collections_page(*, collections: list[dict]) -> dict:
    featured = [c for c in collections if c.get("featured")]
    regular = [c for c in collections if not c.get("featured")]
    total_apps = sum(c.get("app_count", 0) for c in collections)
    return {"featured": featured, "collections": regular,
            "total": len(collections), "total_apps": total_apps}
