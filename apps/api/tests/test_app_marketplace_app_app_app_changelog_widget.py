from app.services.app_marketplace_app_app_app_changelog_widget import build_changelog_widget

def test_widget():
    entries = [
        {"version": "2.1.0", "title": "Dark mode", "type": "added", "date": "2026-10-20"},
        {"version": "2.0.1", "title": "Login fix", "type": "fixed", "date": "2026-10-15"},
    ]
    r = build_changelog_widget(app_name="SuperApp", entries=entries)
    assert r["shown"] == 2
    assert r["entries"][0]["icon"] == "✨"
    assert not r["has_more"]

def test_has_more():
    entries = [{"title": f"Entry {i}"} for i in range(10)]
    r = build_changelog_widget(app_name="X", entries=entries, max_entries=3)
    assert r["shown"] == 3
    assert r["has_more"]
