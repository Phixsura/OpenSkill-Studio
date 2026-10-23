from app.services.app_marketplace_app_app_kbd_shortcut import format_shortcut

def test_mac():
    r = format_shortcut(keys=["cmd", "shift", "k"], platform="mac")
    assert r["display"] == "⌘⇧K"

def test_windows():
    r = format_shortcut(keys=["cmd", "shift", "k"], platform="windows")
    assert r["display"] == "Ctrl+Shift+K"

def test_simple():
    r = format_shortcut(keys=["escape"], platform="mac")
    assert r["display"] == "⎋"
