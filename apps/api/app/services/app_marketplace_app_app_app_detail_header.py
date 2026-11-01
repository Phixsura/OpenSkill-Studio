"""App detail header — top section of the app detail page."""

import html


def build_app_detail_header(*, app: dict) -> dict:
    safe_name = html.escape(app.get("name", ""))
    safe_dev = html.escape(app.get("developer", ""))
    rating = app.get("avg_rating", 0)
    installs = app.get("install_count", 0)
    price = app.get("price", 0)
    return {
        "name": safe_name,
        "developer": safe_dev,
        "tagline": html.escape(app.get("tagline", "")),
        "icon_letter": safe_name[0] if safe_name else "?",
        "rating": round(rating, 1),
        "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
        "review_count": app.get("review_count", 0),
        "install_count": installs,
        "install_display": f"{installs // 1000}K+" if installs >= 1000 else str(installs),
        "price_label": "Free" if price == 0 else f"${price:.2f}/mo",
        "category": app.get("category", ""),
        "verified": app.get("verified_developer", False),
        "version": app.get("version", ""),
    }
