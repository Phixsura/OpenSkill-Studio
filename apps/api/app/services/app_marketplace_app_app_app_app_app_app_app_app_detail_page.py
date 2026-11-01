"""App detail page builder — assemble all data for a marketplace app detail page."""
from __future__ import annotations
import html


def build_app_detail(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    desc = html.escape(app.get("description", "")[:500])
    rating = app.get("rating", 0)
    installs = app.get("installs", 0)
    stars = "★" * int(rating) + "☆" * (5 - int(rating))
    return {
        "name": name, "tagline": html.escape(app.get("tagline", "")[:100]),
        "description": desc, "long_description": html.escape(app.get("long_description", "")[:2000]),
        "icon": app.get("icon", "📱"), "category": app.get("category", ""),
        "developer": html.escape(app.get("developer", "")),
        "website": app.get("website", ""), "support_url": app.get("support_url", ""),
        "rating": rating, "stars": stars, "review_count": app.get("review_count", 0),
        "installs": installs, "installs_display": f"{installs:,}",
        "version": app.get("version", "1.0.0"),
        "verified": app.get("verified", False),
        "price_type": app.get("price_type", "free"),
        "price_display": "Free" if app.get("price_type") == "free" else f"${app.get('price', 0)}/mo",
        "permissions": app.get("permissions", []),
        "screenshots": app.get("screenshots", []),
        "tags": app.get("tags", []),
        "updated": app.get("updated", ""),
        "size": app.get("size", ""),
    }
