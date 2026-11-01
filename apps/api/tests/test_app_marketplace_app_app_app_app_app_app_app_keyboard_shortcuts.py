from app.services.app_marketplace_app_app_app_app_app_app_app_keyboard_shortcuts import get_shortcuts, get_by_category, find_shortcut

def test_shortcuts():
    all_s = get_shortcuts()
    assert len(all_s) == 8
    nav = get_shortcuts(category="navigation")
    assert all(s["category"] == "navigation" for s in nav)

def test_by_category():
    cats = get_by_category()
    assert "navigation" in cats
    assert "actions" in cats

def test_find():
    s = find_shortcut("⌘K")
    assert s is not None
    assert s["action"] == "open_command_palette"
    assert find_shortcut("⌘Z") is None
