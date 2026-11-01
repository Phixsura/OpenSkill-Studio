from app.services.app_marketplace_app_app_app_changelog_feed import build_changelog_feed

def test_feed():
    changelogs = [
        {"app_name": "AppA", "app_icon": "🚀", "entries": [
            {"version": "2.0", "title": "Dark mode", "type": "added", "date": "2026-03-01"},
        ]},
        {"app_name": "AppB", "app_icon": "📦", "entries": [
            {"version": "1.5", "title": "Bug fix", "type": "fixed", "date": "2026-03-02"},
        ]},
    ]
    r = build_changelog_feed(apps_changelogs=changelogs)
    assert r["total"] == 2
    assert r["entries"][0]["app_name"] == "AppB"  # newest first
    assert r["apps_with_updates"] == 2
