from app.services.app_marketplace_app_app_app_notifications_page import build_notifications_page

def test_page():
    notifs = [
        {"id": "1", "title": "App installed", "category": "apps", "read": False, "icon": "📦"},
        {"id": "2", "title": "New review", "category": "reviews", "read": True, "icon": "⭐"},
        {"id": "3", "title": "Deploy done", "category": "apps", "read": False, "icon": "🚀"},
    ]
    r = build_notifications_page(notifications=notifs)
    assert r["total"] == 3
    assert r["unread"] == 2
    assert len(r["tabs"]) == 2
    apps_tab = next(t for t in r["tabs"] if t["id"] == "apps")
    assert apps_tab["count"] == 2
    assert apps_tab["unread"] == 2
