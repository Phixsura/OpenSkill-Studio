from app.services.app_marketplace_app_app_app_app_app_app_app_api_changelog import record_change, build_api_changelog

def test_record():
    r = record_change("2.0", "added", "/api/v2/users", "New users endpoint")
    assert r["recorded"]
    r2 = record_change("2.0", "invalid", "/x", "bad")
    assert not r2["recorded"]

def test_changelog():
    changes = [
        record_change("2.0", "added", "/users", "New endpoint"),
        record_change("2.0", "removed", "/legacy", "Removed", breaking=True),
        record_change("1.5", "fixed", "/auth", "Bug fix"),
    ]
    r = build_api_changelog(changes)
    assert r["version_count"] == 2
    assert r["total_changes"] == 3
    assert r["breaking_count"] == 1
    assert r["has_breaking"]
