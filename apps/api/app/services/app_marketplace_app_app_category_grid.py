"""Category grid — browse marketplace categories."""


CATEGORIES = [
    {"id": "tools", "name": "Developer Tools", "icon": "🔧", "count": 85, "color": "blue"},
    {"id": "analytics", "name": "Analytics", "icon": "📊", "count": 62, "color": "purple"},
    {"id": "security", "name": "Security", "icon": "🔒", "count": 48, "color": "red"},
    {"id": "communication", "name": "Communication", "icon": "💬", "count": 55, "color": "green"},
    {"id": "design", "name": "Design", "icon": "🎨", "count": 40, "color": "pink"},
    {"id": "productivity", "name": "Productivity", "icon": "📋", "count": 72, "color": "yellow"},
    {"id": "infrastructure", "name": "Infrastructure", "icon": "🏗️", "count": 35, "color": "orange"},
    {"id": "ai_ml", "name": "AI & Machine Learning", "icon": "🤖", "count": 28, "color": "cyan"},
    {"id": "payments", "name": "Payments", "icon": "💳", "count": 32, "color": "emerald"},
    {"id": "monitoring", "name": "Monitoring", "icon": "📡", "count": 25, "color": "indigo"},
    {"id": "testing", "name": "Testing", "icon": "🧪", "count": 20, "color": "violet"},
    {"id": "database", "name": "Database", "icon": "💾", "count": 30, "color": "amber"},
]


def get_categories(*, sort_by: str = "count") -> dict:
    sorted_cats = sorted(CATEGORIES, key=lambda c: c.get(sort_by, 0),
                          reverse=sort_by == "count")
    total_apps = sum(c["count"] for c in CATEGORIES)
    return {"categories": sorted_cats, "total_categories": len(sorted_cats),
            "total_apps": total_apps}


def get_category(*, category_id: str) -> dict:
    cat = next((c for c in CATEGORIES if c["id"] == category_id), None)
    if not cat:
        return {"error": f"Category not found: {category_id}"}
    return {**cat, "found": True}
