"""Marketplace app page — the complete marketplace app detail page."""

import html


def build_marketplace_app_page(*, app: dict, developer: dict,
                                  stats: dict, installed: bool = False) -> dict:
    rating = stats.get("avg_rating", 0)
    return {
        "app": {
            "id": app.get("id", ""),
            "name": html.escape(app.get("name", "")),
            "icon": app.get("icon", "📦"),
            "tagline": html.escape(app.get("tagline", "")),
            "description": html.escape(app.get("description", "")),
            "version": app.get("version", "1.0.0"),
            "pricing": app.get("pricing", "Free"),
            "categories": app.get("categories", []),
            "tags": app.get("tags", []),
        },
        "developer": {
            "name": html.escape(developer.get("name", "")),
            "verified": developer.get("verified", False),
            "app_count": developer.get("app_count", 0),
        },
        "stats": {
            "installs": stats.get("installs", 0),
            "rating": rating,
            "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
            "review_count": stats.get("review_count", 0),
        },
        "installed": installed,
        "cta": "Open" if installed else "Install" if app.get("pricing") == "Free" else f"Subscribe — {app.get('pricing', '')}",
    }
