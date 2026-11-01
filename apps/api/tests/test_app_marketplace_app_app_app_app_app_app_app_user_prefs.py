from app.services.app_marketplace_app_app_app_app_app_app_app_user_prefs import (
    get_prefs, set_pref, reset_prefs, clear_all_prefs,
)

def test_defaults():
    clear_all_prefs()
    r = get_prefs("u1")
    assert r["preferences"]["theme"] == "system"
    assert r["customized"] == 0

def test_set():
    clear_all_prefs()
    set_pref("u1", "theme", "dark")
    r = get_prefs("u1")
    assert r["preferences"]["theme"] == "dark"
    assert r["customized"] == 1
    r2 = set_pref("u1", "bad_key", "x")
    assert not r2["set"]
    clear_all_prefs()

def test_reset():
    clear_all_prefs()
    set_pref("u1", "theme", "dark")
    reset_prefs("u1")
    r = get_prefs("u1")
    assert r["preferences"]["theme"] == "system"
    clear_all_prefs()
