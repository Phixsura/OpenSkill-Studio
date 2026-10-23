from app.services.app_marketplace_app_app_quick_settings import get_quick_settings, reset_setting

def test_defaults():
    r = get_quick_settings()
    assert r["total"] == 6
    assert r["modified_count"] == 0
    assert r["settings"]["dark_mode"]["value"] == "system"

def test_overrides():
    r = get_quick_settings(overrides={"dark_mode": "dark", "language": "ja"})
    assert r["settings"]["dark_mode"]["value"] == "dark"
    assert r["settings"]["dark_mode"]["modified"]
    assert r["modified_count"] == 2

def test_reset():
    r = reset_setting(key="dark_mode")
    assert r["reset"]
    assert r["value"] == "system"

def test_reset_unknown():
    r = reset_setting(key="nonexistent")
    assert "error" in r
