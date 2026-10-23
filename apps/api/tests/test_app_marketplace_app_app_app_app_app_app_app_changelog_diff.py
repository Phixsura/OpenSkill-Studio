from app.services.app_marketplace_app_app_app_app_app_app_app_changelog_diff import diff_versions

def test_diff():
    v1 = [
        {"method": "GET", "path": "/users"},
        {"method": "POST", "path": "/users"},
        {"method": "GET", "path": "/legacy"},
    ]
    v2 = [
        {"method": "GET", "path": "/users"},
        {"method": "POST", "path": "/users", "body": "changed"},
        {"method": "GET", "path": "/exports"},
    ]
    r = diff_versions(v1, v2)
    assert r["added_count"] == 1
    assert r["removed_count"] == 1
    assert r["changed_count"] == 1
    assert r["breaking"]
    assert r["summary"] == "+1 -1 ~1"
