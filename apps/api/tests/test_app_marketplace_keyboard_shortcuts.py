from app.services.app_marketplace_keyboard_shortcuts import get_shortcuts, find_shortcut, get_shortcuts_by_scope

def test_all():
    s = get_shortcuts()
    assert len(s) >= 9

def test_scope():
    s = get_shortcuts(scope="dashboard")
    assert all(x["scope"] in ("dashboard", "global") for x in s)

def test_find():
    s = find_shortcut(key="Ctrl+K")
    assert s["action"] == "open_command_palette"

def test_not_found():
    assert find_shortcut(key="Ctrl+Z") is None

def test_by_scope():
    g = get_shortcuts_by_scope()
    assert "global" in g
    assert len(g["global"]) >= 3
