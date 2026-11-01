from app.services.app_marketplace_app_app_accordion import build_accordion

def test_basic():
    sections = [
        {"title": "Getting Started", "content": "Install the SDK..."},
        {"title": "Configuration", "content": "Set your API key..."},
        {"title": "FAQ", "content": "Common questions...", "icon": "❓"},
    ]
    r = build_accordion(sections=sections, default_open=[0])
    assert r["total"] == 3
    assert r["items"][0]["open"]
    assert not r["items"][1]["open"]
    assert r["open_count"] == 1

def test_multiple():
    r = build_accordion(sections=[{"title": "A"}, {"title": "B"}],
        allow_multiple=True, default_open=[0, 1])
    assert r["allow_multiple"]
    assert r["open_count"] == 2
