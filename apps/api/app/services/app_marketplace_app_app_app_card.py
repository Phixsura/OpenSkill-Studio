"""App card — compact app listing card builder."""

import html


def build_app_card(*, app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    desc = html.escape(app.get("description", ""))
    short = desc[:80] + "..." if len(desc) > 80 else desc
    rating = app.get("rating", 0)
    return {
        "id": app.get("id", ""),
        "name": name,
        "short_description": short,
        "icon": app.get("icon", "📦"),
        "rating": rating,
        "stars": "★" * round(rating) + "☆" * (5 - round(rating)),
        "downloads": app.get("downloads", 0),
        "downloads_display": _compact(app.get("downloads", 0)),
        "category": app.get("category", ""),
        "verified": app.get("verified", False),
        "pricing": app.get("pricing", "Free"),
    }


def _compact(n: int) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(n)


def build_app_grid(*, apps: list[dict]) -> dict:
    cards = [build_app_card(app=a) for a in apps]
    categories = sorted(set(c["category"] for c in cards if c["category"]))
    return {"cards": cards, "total": len(cards), "categories": categories}
