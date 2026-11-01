"""App preview builder — build app preview card with all display data."""

def build_preview(app: dict, *, developer: dict | None = None, badges: list[str] | None = None) -> dict:
    return {
        "id": app.get("id"), "name": app.get("name"), "slug": app.get("slug"),
        "description": (app.get("description") or "")[:120],
        "category": app.get("category"), "icon": app.get("icon_url"),
        "developer_name": developer.get("display_name") if developer else None,
        "verified": developer.get("verified", False) if developer else False,
        "install_count": app.get("install_count", 0),
        "badges": badges or [],
    }
