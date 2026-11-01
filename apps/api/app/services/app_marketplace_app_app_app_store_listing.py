"""App store listing — complete marketplace listing builder."""

import html
from datetime import datetime, timezone


def build_store_listing(*, app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    desc = html.escape(app.get("description", ""))
    short_desc = desc[:120] + "..." if len(desc) > 120 else desc
    screenshots = app.get("screenshots", [])
    reviews = app.get("reviews", [])
    avg_rating = round(sum(r.get("rating", 0) for r in reviews) / max(len(reviews), 1), 1) if reviews else 0
    stars = "★" * int(avg_rating) + "☆" * (5 - int(avg_rating))
    return {
        "name": name,
        "short_description": short_desc,
        "full_description": desc,
        "icon": app.get("icon", "📦"),
        "category": app.get("category", "Utilities"),
        "version": app.get("version", "1.0.0"),
        "author": html.escape(app.get("author", "")),
        "downloads": app.get("downloads", 0),
        "avg_rating": avg_rating,
        "stars_display": stars,
        "review_count": len(reviews),
        "screenshot_count": len(screenshots),
        "pricing": app.get("pricing", "Free"),
        "tags": app.get("tags", []),
        "updated_at": app.get("updated_at", datetime.now(timezone.utc).isoformat()),
        "verified": app.get("verified", False),
    }
