from app.services.app_marketplace_app_notification_preferences import get_default_preferences, update_preference, should_notify

def test_defaults():
    p = get_default_preferences()
    assert len(p) == 6
    assert p["installs"]["enabled"]

def test_update():
    prefs = get_default_preferences()
    r = update_preference(preferences=prefs, category="reviews", channels=["slack"], enabled=True)
    assert r["preferences"]["reviews"]["channels"] == ["slack"]

def test_invalid_category():
    r = update_preference(preferences={}, category="magic", channels=[], enabled=True)
    assert r["error"]

def test_should_notify():
    prefs = {"errors": {"channels": ["email", "slack"], "enabled": True}}
    assert should_notify(preferences=prefs, category="errors", channel="email")
    assert not should_notify(preferences=prefs, category="errors", channel="webhook")

def test_disabled():
    prefs = {"errors": {"channels": ["email"], "enabled": False}}
    assert not should_notify(preferences=prefs, category="errors", channel="email")
