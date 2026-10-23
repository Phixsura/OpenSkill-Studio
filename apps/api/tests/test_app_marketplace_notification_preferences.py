from app.services.app_marketplace_notification_preferences import (
    get_notification_preferences, update_notification_preference)

def test_get():
    r = get_notification_preferences(user_id="u1")
    assert len(r["channels"]) == 4
    assert len(r["categories"]) == 5
    assert r["preferences"]["app_updates"]["email"] is True
    assert r["preferences"]["marketing"]["push"] is False

def test_update():
    r = update_notification_preference(user_id="u1", category="billing", channel="email", enabled=False)
    assert r["success"]

def test_locked():
    r = update_notification_preference(user_id="u1", category="security_alerts", channel="email", enabled=False)
    assert not r["success"]
    assert "cannot be disabled" in r["error"]
