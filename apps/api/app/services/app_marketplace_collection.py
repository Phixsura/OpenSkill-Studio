"""Marketplace collections — curated app collections."""

_collections: dict[str, dict] = {}


def create_collection(*, slug: str, title: str, description: str, app_ids: list[str]) -> dict:
    c = {"slug": slug, "title": title, "description": description, "app_ids": app_ids, "app_count": len(app_ids)}
    _collections[slug] = c
    return c


def get_collection(slug: str) -> dict | None:
    return _collections.get(slug)


def list_collections() -> list[dict]:
    return sorted(_collections.values(), key=lambda c: c["title"])


def add_to_collection(slug: str, app_id: str) -> bool:
    c = _collections.get(slug)
    if not c: return False
    if app_id not in c["app_ids"]:
        c["app_ids"].append(app_id)
        c["app_count"] = len(c["app_ids"])
    return True
