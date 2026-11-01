from app.services.app_marketplace_app_app_app_app_app_changelog_page_v2 import build_platform_changelog

def test_changelog():
    entries = [
        {"service": "API", "title": "New endpoint", "type": "added", "date": "2026-10-01"},
        {"service": "API", "title": "Fixed auth bug", "type": "fixed", "date": "2026-10-02"},
        {"service": "Web", "title": "Dark mode", "type": "added", "date": "2026-10-01"},
    ]
    r = build_platform_changelog(entries=entries)
    assert r["total_entries"] == 3
    assert r["service_count"] == 2
    api = next(s for s in r["sections"] if s["service"] == "API")
    assert api["count"] == 2
