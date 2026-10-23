from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_rss import generate_rss, parse_entries

def test_rss():
    entries = [{"title": "v2.0", "description": "Major update", "date": "2024-01-01", "id": "2.0"}]
    r = generate_rss("My App Changelog", "https://app.com/changelog", entries)
    assert "<title>My App Changelog</title>" in r["xml"]
    assert "<title>v2.0</title>" in r["xml"]
    assert r["item_count"] == 1

def test_escape():
    entries = [{"title": "<script>", "description": "a&b", "date": "", "id": "1"}]
    r = generate_rss("Test", "https://x.com", entries)
    assert "<script>" not in r["xml"]
    assert "&amp;" in r["xml"]

def test_parse():
    releases = [{"version": "2.0", "summary": "New features", "date": "2024-01-01"}]
    entries = parse_entries(releases)
    assert entries[0]["title"] == "v2.0"
