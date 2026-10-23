from app.services.app_marketplace_app_app_user_preference import get_preferences, validate_preference

def test_defaults():
    r = get_preferences()
    assert r["preferences"]["theme"] == "system"
    assert r["preferences"]["code_font_size"] == 14

def test_override():
    r = get_preferences(overrides={"theme": "dark", "compact_view": True})
    assert r["preferences"]["theme"] == "dark"
    assert r["preferences"]["compact_view"]

def test_validate_ok():
    assert validate_preference(key="theme", value="dark")["valid"]

def test_validate_bad_type():
    assert not validate_preference(key="code_font_size", value="big")["valid"]

def test_validate_bad_theme():
    assert not validate_preference(key="theme", value="neon")["valid"]
