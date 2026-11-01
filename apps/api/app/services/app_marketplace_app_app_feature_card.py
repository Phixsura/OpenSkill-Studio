"""Feature card — showcase individual platform features."""

import html


def build_feature_cards(*, features: list[dict]) -> dict:
    cards = []
    for f in features:
        cards.append({
            "title": html.escape(f.get("title", "")),
            "description": html.escape(f.get("description", "")),
            "icon": f.get("icon", "⚡"),
            "category": f.get("category", "general"),
            "link": f.get("link"),
        })
    categories = sorted(set(c["category"] for c in cards))
    return {"cards": cards, "total": len(cards), "categories": categories}
