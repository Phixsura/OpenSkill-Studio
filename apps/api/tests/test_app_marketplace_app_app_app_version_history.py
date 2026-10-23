from app.services.app_marketplace_app_app_app_version_history import build_version_history

def test_history():
    versions = [
        {"version": "1.0.0", "published_at": "2026-01-01", "author": "Alice", "change_count": 5, "downloads": 1000},
        {"version": "2.0.0", "published_at": "2026-03-01", "author": "Bob", "change_count": 12, "downloads": 500},
        {"version": "2.1.0-beta.1", "published_at": "2026-04-01", "author": "Alice", "change_count": 3},
    ]
    r = build_version_history(versions=versions)
    assert r["total"] == 3
    assert r["latest"] == "2.1.0-beta.1"
    assert r["versions"][0]["is_latest"]
    assert r["prerelease_count"] == 1
