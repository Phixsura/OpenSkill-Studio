"""App card builder — render marketplace app cards with consistent layout."""
from __future__ import annotations
import html


def build_app_card(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    desc = html.escape(app.get("description", "")[:150])
    rating = app.get("rating", 0)
    installs = app.get("installs", 0)
    stars = "⭐" * int(rating) + "☆" * (5 - int(rating))
    install_display = f"{installs:,}" if installs < 1000000 else f"{installs / 1000000:.1f}M"
    return {
        "name": name, "description": desc,
        "icon": app.get("icon", "📱"),
        "category": app.get("category", ""),
        "rating": rating, "stars": stars,
        "installs": installs, "install_display": install_display,
        "verified": app.get("verified", False),
        "price_type": app.get("price_type", "free"),
        "price_display": "Free" if app.get("price_type") == "free" else f"${app.get('price', 0)}/mo",
        "developer": app.get("developer", ""),
    }


def build_card_grid(apps: list[dict]) -> dict:
    cards = [build_app_card(a) for a in apps]
    return {"cards": cards, "total": len(cards)}
