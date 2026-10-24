"""Featured collections — curated app groups for marketplace homepage."""

from datetime import datetime, timezone


def create_collection(*, title: str, description: str, slug: str, apps: list[dict],
                        curator_id: str) -> dict:
    return {
        "slug": slug, "title": title, "description": description,
        "app_ids": [a["id"] for a in apps], "app_count": len(apps),
        "curator_id": curator_id, "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def publish_collection(*, collection: dict) -> dict:
    if collection.get("app_count", 0) < 3:
        return {"error": "Collection needs at least 3 apps", "published": False}
    return {**collection, "status": "published", "published_at": datetime.now(timezone.utc).isoformat(), "published": True}


def build_collection_card(*, collection: dict, apps: list[dict]) -> dict:
    previews = apps[:4]
    return {
        "slug": collection["slug"], "title": collection["title"],
        "description": collection["description"], "app_count": collection["app_count"],
        "preview_apps": [{"id": a["id"], "name": a["name"], "icon": a.get("icon")} for a in previews],
    }
