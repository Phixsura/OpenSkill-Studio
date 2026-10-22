"""Marketplace newsletter — build newsletter content from recent activity."""

def build_newsletter(*, period: str, new_apps: list[dict], trending: list[dict], updates: list[dict]) -> dict:
    return {
        "period": period,
        "sections": [
            {"title": "🆕 New Apps", "items": new_apps[:5]},
            {"title": "🔥 Trending", "items": trending[:5]},
            {"title": "🔄 Recent Updates", "items": updates[:5]},
        ],
        "total_items": len(new_apps) + len(trending) + len(updates),
    }
