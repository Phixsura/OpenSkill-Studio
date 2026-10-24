from app.services.app_marketplace_app_app_notification_center import build_notification_center, mark_read

def test_build():
    notifs = [
        {"id": "1", "title": "New review", "body": "Alice reviewed your app", "read": False, "timestamp": "2026-01-02T00:00:00Z"},
        {"id": "2", "title": "Published", "body": "App v2 published", "read": True, "timestamp": "2026-01-01T00:00:00Z"},
    ]
    r = build_notification_center(notifications=notifs)
    assert r["total"] == 2
    assert r["unread"] == 1
    assert r["notifications"][0]["title"] == "New review"  # newest first

def test_mark_read():
    notifs = [{"id": "1", "read": False}, {"id": "2", "read": False}]
    r = mark_read(notifications=notifs, ids=["1"])
    assert r["updated"] == 1
    assert notifs[0]["read"]
    assert not notifs[1]["read"]
