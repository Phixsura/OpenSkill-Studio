from app.services.app_marketplace_app_keyboard_shortcut import get_shortcuts, find_shortcut

def test_all():
    r = get_shortcuts()
    assert r["total"] == 7
    assert len(r["categories"]) >= 3

def test_filter():
    r = get_shortcuts(category="navigation")
    assert all(s["category"] == "navigation" for s in r["shortcuts"])

def test_find():
    r = find_shortcut(key="Cmd+K")
    assert r["found"]
    assert r["action"] == "search"

def test_not_found():
    r = find_shortcut(key="Ctrl+Z")
    assert not r["found"]
