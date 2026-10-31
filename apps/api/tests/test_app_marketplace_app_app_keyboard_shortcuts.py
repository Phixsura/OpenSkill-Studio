from app.services.app_marketplace_app_app_keyboard_shortcuts import register_shortcuts

def test_register():
    shortcuts = [
        {"combo": "Ctrl+S", "action": "Save", "context": "editor"},
        {"combo": "Ctrl+K", "action": "Search", "context": "global"},
        {"combo": "Escape", "action": "Close", "context": "modal"},
    ]
    r = register_shortcuts(shortcuts=shortcuts)
    assert r["total"] == 3
    assert r["context_count"] == 3
    assert len(r["conflicts"]) == 0

def test_conflict():
    shortcuts = [
        {"combo": "Ctrl+S", "action": "Save", "context": "editor"},
        {"combo": "Ctrl+S", "action": "Search", "context": "editor"},
    ]
    r = register_shortcuts(shortcuts=shortcuts)
    assert len(r["conflicts"]) == 1
