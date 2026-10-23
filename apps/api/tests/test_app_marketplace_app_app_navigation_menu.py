from app.services.app_marketplace_app_app_navigation_menu import build_nav_menu

def test_nav():
    items = [
        {"label": "Dashboard", "path": "/dashboard", "icon": "🏠", "section": "main"},
        {"label": "Apps", "path": "/apps", "icon": "📦", "section": "main"},
        {"label": "Settings", "path": "/settings", "icon": "⚙️", "section": "admin"},
    ]
    r = build_nav_menu(items=items, active_path="/apps")
    assert r["total_items"] == 3
    assert r["section_count"] == 2
    assert r["sections"]["main"][1]["active"]
