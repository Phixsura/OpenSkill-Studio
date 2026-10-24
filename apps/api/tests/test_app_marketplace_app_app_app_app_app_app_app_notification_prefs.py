from app.services.app_marketplace_app_app_app_app_app_app_app_notification_prefs import (
    default_prefs, update_prefs, summarize_prefs)

def test_defaults():
    p = default_prefs()
    assert p["security"]["email"] is True
    assert p["marketing"]["email"] is False

def test_update():
    p = default_prefs()
    r = update_prefs(p, category="security", channel="push", enabled=False)
    assert r["status"] == "updated"
    assert p["security"]["push"] is False

def test_summarize():
    p = default_prefs()
    s = summarize_prefs(p)
    assert s["total_settings"] == 24  # 6 categories * 4 channels
    assert "marketing" in s["muted_categories"]
    assert s["enabled"] == 20  # all except 4 marketing channels
