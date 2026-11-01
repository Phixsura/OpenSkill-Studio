from app.services.app_marketplace_app_user_preference import get_preferences, update_preference

def test_defaults():
    r = get_preferences()
    assert r["total"] == 7
    assert r["preferences"]["theme"]["value"] == "system"
    assert r["preferences"]["theme"]["is_default"]

def test_overrides():
    r = get_preferences(overrides={"theme": "dark"})
    assert r["preferences"]["theme"]["value"] == "dark"
    assert not r["preferences"]["theme"]["is_default"]

def test_update():
    r = update_preference(key="theme", value="dark")
    assert r["updated"]

def test_invalid_value():
    r = update_preference(key="theme", value="rainbow")
    assert "error" in r

def test_unknown_key():
    r = update_preference(key="nonexistent", value="x")
    assert "error" in r
