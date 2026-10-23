from app.services.app_marketplace_app_app_app_category_page import build_category_page

def test_category():
    category = {"id": "tools", "name": "Developer Tools", "icon": "🔧", "description": "Build faster"}
    apps = [
        {"id": "a1", "name": "Editor", "downloads": 5000, "rating": 4.5},
        {"id": "a2", "name": "Linter", "downloads": 8000, "rating": 4.2},
    ]
    r = build_category_page(category=category, apps=apps, sort_by="popular")
    assert r["category"]["name"] == "Developer Tools"
    assert r["total"] == 2
    assert r["apps"][0]["name"] == "Linter"  # more downloads
