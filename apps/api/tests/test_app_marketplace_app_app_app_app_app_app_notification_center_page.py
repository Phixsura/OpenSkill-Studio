from app.services.app_marketplace_app_app_app_app_app_app_notification_center_page import build_notification_center_page

def test_center():
    notifs = [
        {"id": "1", "title": "App installed", "category": "apps", "read": False, "icon": "📦"},
        {"id": "2", "title": "Review posted", "category": "reviews", "read": True, "icon": "⭐"},
        {"id": "3", "title": "Deploy done", "category": "apps", "read": False, "icon": "🚀"},
    ]
    r = build_notification_center_page(notifications=notifs)
    assert r["total"] == 3
    assert r["unread"] == 2
    assert r["has_unread"]
    assert len(r["categories"]) == 2
    apps_cat = next(c for c in r["categories"] if c["id"] == "apps")
    assert apps_cat["unread"] == 2
