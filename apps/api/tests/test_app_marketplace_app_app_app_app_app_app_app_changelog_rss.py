from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_rss import build_changelog_rss

def test_rss():
    r = build_changelog_rss([
        {"title": "v3.5 Released", "version": "3.5.0", "date": "2026-10-24", "description": "SSO and dark mode", "change_count": 15},
        {"title": "v3.4.1 Patch", "version": "3.4.1", "date": "2026-10-20", "description": "Bug fixes", "change_count": 3},
    ])
    assert r["item_count"] == 2
    assert r["last_updated"] == "2026-10-24"
    assert "changelog/3.5.0" in r["items"][0]["link"]
