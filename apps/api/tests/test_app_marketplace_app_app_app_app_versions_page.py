from app.services.app_marketplace_app_app_app_app_versions_page import build_versions_page

def test_versions():
    versions = [
        {"version": "1.0.0", "published_at": "2026-01-01", "author": "Alice", "downloads": 5000, "change_count": 10, "status": "published"},
        {"version": "2.0.0", "published_at": "2026-03-01", "author": "Bob", "downloads": 2000, "change_count": 15, "status": "published"},
        {"version": "2.1.0-beta", "published_at": "2026-04-01", "author": "Alice", "downloads": 50, "change_count": 3, "status": "published"},
    ]
    r = build_versions_page(app_name="SuperApp", versions=versions, current_version="2.0.0")
    assert r["total"] == 3
    assert r["latest"] == "2.1.0-beta"
    assert r["prerelease_count"] == 1
    assert r["total_downloads"] == 7050
    assert r["versions"][1]["is_current"]  # 2.0.0 is current (sorted by date desc: beta, 2.0, 1.0)
    assert r["versions"][2]["can_rollback"]  # 1.0.0 can rollback
