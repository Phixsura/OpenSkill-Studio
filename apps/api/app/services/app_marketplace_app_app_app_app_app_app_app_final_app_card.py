"""Final app card — the definitive marketplace app card format."""
from __future__ import annotations
import html


def build_final_card(app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    rating = app.get("rating", 0)
    installs = app.get("installs", 0)
    return {
        "name": name,
        "icon": app.get("icon", "📱"),
        "tagline": html.escape(app.get("tagline", "")[:80]),
        "developer": html.escape(app.get("developer", "")),
        "rating": rating,
        "stars": "★" * int(rating) + "☆" * (5 - int(rating)),
        "installs_display": f"{installs:,}" if installs < 1_000_000 else f"{installs/1_000_000:.1f}M",
        "price_display": "Free" if app.get("price_type") == "free" else f"${app.get('price', 0)}/mo",
        "verified": app.get("verified", False),
        "category": app.get("category", ""),
        "badges": [b for b in app.get("badges", [])],
    }
