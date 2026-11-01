from app.services.app_marketplace_notif_prefs_v2 import get_default_preferences, update_preferences, should_send

def test_defaults():
    p = get_default_preferences()
    assert len(p) == 7
    assert p["error.spike"]["enabled"]
    assert "slack" in p["error.spike"]["channels"]

def test_update():
    prefs = get_default_preferences()
    r = update_preferences(current=prefs, event_type="review.created", channels=["slack"], enabled=True)
    assert r["review.created"]["channels"] == ["slack"]

def test_update_invalid_event():
    r = update_preferences(current={}, event_type="unknown", channels=[], enabled=True)
    assert "_error" in r

def test_should_send():
    prefs = {"error.spike": {"channels": ["email", "slack"], "enabled": True}}
    assert should_send(preferences=prefs, event_type="error.spike", channel="email")
    assert not should_send(preferences=prefs, event_type="error.spike", channel="webhook")

def test_disabled():
    prefs = {"error.spike": {"channels": ["email"], "enabled": False}}
    assert not should_send(preferences=prefs, event_type="error.spike", channel="email")
