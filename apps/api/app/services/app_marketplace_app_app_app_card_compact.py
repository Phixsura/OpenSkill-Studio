"""App card compact — compact app card for lists and grids."""

import html


def build_compact_card(*, app: dict) -> dict:
    name = html.escape(app.get("name", ""))
    dev = html.escape(app.get("developer", ""))
    rating = app.get("rating", 0)
    installs = app.get("installs", 0)
    price = app.get("price", 0)
    return {
        "id": app.get("id", ""),
        "name": name,
        "developer": dev,
        "icon_letter": name[0].upper() if name else "?",
        "rating": round(rating, 1),
        "stars_display": "★" * round(rating) + "☆" * (5 - round(rating)),
        "install_display": f"{installs // 1000}K+" if installs >= 1000 else str(installs),
        "price_label": "Free" if price == 0 else f"${price:.2f}",
        "category": app.get("category", ""),
    }


def build_card_list(*, apps: list[dict]) -> dict:
    cards = [build_compact_card(app=a) for a in apps]
    return {"cards": cards, "total": len(cards)}
