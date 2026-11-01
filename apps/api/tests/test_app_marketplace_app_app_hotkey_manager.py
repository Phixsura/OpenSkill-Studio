from app.services.app_marketplace_app_app_hotkey_manager import build_hotkey_registry

def test_registry():
    shortcuts = [
        {"combo": "Ctrl+S", "action": "Save", "category": "File"},
        {"combo": "Ctrl+N", "action": "New", "category": "File"},
        {"combo": "Ctrl+P", "action": "Preview", "category": "View"},
    ]
    r = build_hotkey_registry(shortcuts=shortcuts)
    assert r["total"] == 3
    assert not r["has_conflicts"]
    assert "File" in r["categories"]
    assert "View" in r["categories"]

def test_conflict():
    shortcuts = [
        {"combo": "Ctrl+S", "action": "Save"},
        {"combo": "Ctrl+S", "action": "Search"},
    ]
    r = build_hotkey_registry(shortcuts=shortcuts)
    assert r["has_conflicts"]
    assert len(r["conflicts"]) == 1
    assert "Save" in r["conflicts"][0]["actions"]
