from app.services.app_marketplace_user_preferences import get_preferences, update_preference, reset_preferences, get_preference_schema

def test_defaults():
    p = get_preferences()
    assert p["theme"] == "system"
    assert p["per_page"] == 24

def test_stored():
    p = get_preferences(stored={"theme": "dark", "per_page": 48})
    assert p["theme"] == "dark"
    assert p["per_page"] == 48
    assert p["sort_by"] == "popular"  # default preserved

def test_update():
    p = get_preferences()
    p = update_preference(current=p, key="theme", value="dark")
    assert p["theme"] == "dark"

def test_update_unknown():
    p = update_preference(current={}, key="magic", value=True)
    assert "_error" in p

def test_reset():
    p = reset_preferences()
    assert p == get_preferences()

def test_schema():
    s = get_preference_schema()
    assert len(s) >= 6
    assert any(x["key"] == "theme" for x in s)
