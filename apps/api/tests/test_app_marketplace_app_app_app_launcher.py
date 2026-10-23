from app.services.app_marketplace_app_app_app_launcher import build_launcher

def test_launcher():
    apps = [
        {"id": "a1", "name": "Slack", "icon": "💬"},
        {"id": "a2", "name": "GitHub", "icon": "🐙"},
        {"id": "a3", "name": "Figma", "icon": "🎨"},
    ]
    r = build_launcher(apps=apps, pinned=["a1"])
    assert r["total"] == 3
    assert r["pinned_count"] == 1
    assert r["apps"][0]["pinned"]
    assert not r["apps"][1]["pinned"]

def test_no_pinned():
    r = build_launcher(apps=[{"id": "x", "name": "App"}])
    assert r["pinned_count"] == 0
