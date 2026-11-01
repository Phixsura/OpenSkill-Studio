from app.services.app_marketplace_app_app_app_app_app_app_app_notif_hub import NotificationHub

def test_send():
    nh = NotificationHub()
    nh.set_preferences("u1", ["email", "slack"])
    r = nh.send("u1", "Deploy complete", "Version 2.0 is live")
    assert r["delivered_to"] == 2
    assert "email" in r["channels"]

def test_stats():
    nh = NotificationHub()
    nh.set_preferences("u1", ["email"])
    nh.send("u1", "Test", "Body")
    s = nh.stats()
    assert s["total_sent"] == 1
    assert s["by_channel"]["email"] == 1
