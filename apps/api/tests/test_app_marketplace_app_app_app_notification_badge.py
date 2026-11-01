from app.services.app_marketplace_app_app_app_notification_badge import build_notification_badge

def test_badge():
    notifs = [
        {"read": False, "category": "apps", "priority": "normal"},
        {"read": False, "category": "apps", "priority": "urgent"},
        {"read": True, "category": "system"},
    ]
    r = build_notification_badge(notifications=notifs)
    assert r["unread"] == 2
    assert r["urgent"] == 1
    assert r["display"] == "2"
    assert r["has_urgent"]
    assert r["by_category"]["apps"] == 2

def test_overflow():
    notifs = [{"read": False, "category": "x"} for _ in range(150)]
    r = build_notification_badge(notifications=notifs)
    assert r["display"] == "99+"

def test_empty():
    r = build_notification_badge(notifications=[])
    assert not r["has_unread"]
