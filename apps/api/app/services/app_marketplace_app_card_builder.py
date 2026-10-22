"""Marketplace app card builder — compile all data needed for an app card."""


def build_app_card(*, app: dict, developer: dict | None = None, badges: list[dict] | None = None,
                    install_count: int = 0, health_score: int = 100, rating: float = 0, rating_count: int = 0) -> dict:
    return {
        "id": app.get("id"), "name": app.get("name"), "slug": app.get("slug"),
        "description": app.get("description"), "icon_url": app.get("icon_url"),
        "category": app.get("category"), "status": app.get("status"),
        "developer": {"name": developer.get("display_name") if developer else None,
                      "verified": developer.get("verified", False) if developer else False},
        "install_count": install_count, "health_score": health_score,
        "rating": rating, "rating_count": rating_count,
        "badges": badges or [],
    }
