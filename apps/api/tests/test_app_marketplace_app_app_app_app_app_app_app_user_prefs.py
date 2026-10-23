from app.services.app_marketplace_app_app_app_app_app_app_app_user_prefs import get_prefs, update_pref, reset_prefs

def test_prefs():
    p = get_prefs("u1", overrides={"theme": "dark"})
    assert p["preferences"]["theme"] == "dark"
    assert p["preferences"]["language"] == "en"

def test_update():
    prefs = dict(get_prefs("u1")["preferences"])
    r = update_pref(prefs, "code_font_size", 16)
    assert r["value"] == 16
    assert prefs["code_font_size"] == 16
    r2 = update_pref(prefs, "unknown_key", True)
    assert "error" in r2

def test_reset():
    r = reset_prefs()
    assert r["reset"]
    assert r["preferences"]["theme"] == "system"
