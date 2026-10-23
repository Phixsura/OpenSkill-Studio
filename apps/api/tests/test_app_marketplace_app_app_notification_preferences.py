from app.services.app_marketplace_app_app_notification_preferences import build_preferences

def test_defaults():
    r = build_preferences()
    assert r["total_events"] == 6
    assert len(r["channels"]) == 4
    assert r["events"][0]["channels"]["email"]

def test_override():
    r = build_preferences(current={"app_installed": {"email": False, "slack": True}})
    ai = next(e for e in r["events"] if e["id"] == "app_installed")
    assert not ai["channels"]["email"]
    assert ai["channels"]["slack"]
