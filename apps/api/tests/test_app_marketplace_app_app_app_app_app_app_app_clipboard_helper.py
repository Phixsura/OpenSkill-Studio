from app.services.app_marketplace_app_app_app_app_app_app_app_clipboard_helper import format_for_copy, build_copy_items

def test_format():
    r = format_for_copy(value="sk_live_abc123def456", label="API Key", sensitive=True)
    assert "••••" in r["display"]
    assert r["copy_text"] == "sk_live_abc123def456"
    assert r["sensitive"]

def test_public():
    r = format_for_copy(value="https://api.example.com", label="Endpoint")
    assert r["display"] == "https://api.example.com"
    assert not r["sensitive"]

def test_batch():
    items = build_copy_items([
        {"value": "key123", "label": "Key", "sensitive": True},
        {"value": "hello", "label": "Msg"},
    ])
    assert len(items) == 2
    assert items[0]["sensitive"]
    assert not items[1]["sensitive"]
