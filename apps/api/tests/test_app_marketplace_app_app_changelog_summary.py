from app.services.app_marketplace_app_app_changelog_summary import summarize_changelog

def test_summary():
    entries = [
        {"type": "added", "title": "Dark mode", "author": "Alice", "highlight": True},
        {"type": "added", "title": "API v3", "author": "Bob"},
        {"type": "fixed", "title": "Login bug", "author": "Alice"},
        {"type": "breaking", "title": "Removed v1 API", "author": "Bob"},
    ]
    r = summarize_changelog(entries=entries, version="3.0.0")
    assert "2 new features" in r["summary"]
    assert "1 bug fix" in r["summary"]
    assert r["has_breaking"]
    assert r["contributor_count"] == 2
    assert "Dark mode" in r["highlights"]

def test_empty():
    r = summarize_changelog(entries=[], version="1.0.0")
    assert r["total_changes"] == 0
