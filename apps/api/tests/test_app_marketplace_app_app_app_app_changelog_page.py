from app.services.app_marketplace_app_app_app_app_changelog_page import build_changelog_page

def test_page():
    releases = [
        {"version": "2.0.0", "date": "2026-03-01", "entries": [
            {"type": "added", "text": "Dark mode"},
            {"type": "fixed", "text": "Login bug"},
        ]},
        {"version": "1.0.0", "date": "2026-01-01", "entries": [
            {"type": "added", "text": "Initial release"},
        ]},
    ]
    r = build_changelog_page(app_name="SuperApp", releases=releases)
    assert r["total_releases"] == 2
    assert r["total_entries"] == 3
    assert r["releases"][0]["version"] == "2.0.0"

def test_filter():
    releases = [{"version": "1.0", "date": "2026-01-01", "entries": [
        {"type": "added", "text": "A"}, {"type": "fixed", "text": "B"}]}]
    r = build_changelog_page(app_name="X", releases=releases, filter_type="fixed")
    assert r["releases"][0]["entry_count"] == 1
