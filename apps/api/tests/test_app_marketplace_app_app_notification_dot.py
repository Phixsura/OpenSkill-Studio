from app.services.app_marketplace_app_app_notification_dot import build_notification_dot

def test_small():
    r = build_notification_dot(count=3)
    assert r["display"] == "3"
    assert r["visible"]
    assert r["size"] == "sm"

def test_over_max():
    r = build_notification_dot(count=25, max_display=9)
    assert r["display"] == "9+"
    assert r["size"] == "md"

def test_zero():
    r = build_notification_dot(count=0)
    assert not r["visible"]
