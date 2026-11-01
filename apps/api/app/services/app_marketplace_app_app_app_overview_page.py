"""App overview page — complete app detail page for marketplace."""

import html


def build_app_overview(*, app: dict, reviews_summary: dict | None = None,
                         changelog: list[dict] | None = None) -> dict:
    name = html.escape(app.get("name", ""))
    rating = app.get("rating", 0)
    return {
        "header": {
            "name": name, "icon": app.get("icon", "📦"),
            "tagline": html.escape(app.get("tagline", "")),
            "author": html.escape(app.get("author", "")),
            "verified": app.get("verified", False),
            "version": app.get("version", "1.0.0"),
        },
        "stats": {
            "downloads": app.get("downloads", 0),
            "rating": rating,
            "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
            "review_count": reviews_summary.get("total", 0) if reviews_summary else 0,
        },
        "description": html.escape(app.get("description", "")),
        "pricing": app.get("pricing", "Free"),
        "categories": app.get("categories", []),
        "tags": app.get("tags", []),
        "screenshots": app.get("screenshots", []),
        "changelog": (changelog or [])[:3],
        "has_changelog": bool(changelog),
        "install_cta": "Install" if app.get("pricing") == "Free" else f"Subscribe ({app.get('pricing', '')})",
    }
