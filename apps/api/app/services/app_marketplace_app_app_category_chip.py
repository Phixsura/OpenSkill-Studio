"""Category chip — category selection chips for filtering."""


CATEGORY_ICONS = {
    "all": "📦", "tools": "🔧", "analytics": "📊", "security": "🔒",
    "communication": "💬", "design": "🎨", "productivity": "📋",
    "infrastructure": "🏗️", "ai_ml": "🤖", "payments": "💳",
}


def build_category_chips(*, categories: list[dict], active: str | None = None) -> dict:
    chips = [{"id": "all", "label": "All", "icon": "📦", "active": active is None, "count": None}]
    for cat in categories:
        chips.append({
            "id": cat["id"],
            "label": cat["name"],
            "icon": CATEGORY_ICONS.get(cat["id"], "📁"),
            "active": cat["id"] == active,
            "count": cat.get("count"),
        })
    return {"chips": chips, "total": len(chips), "active_id": active or "all"}
