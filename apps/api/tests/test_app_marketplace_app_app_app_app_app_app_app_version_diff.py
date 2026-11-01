from app.services.app_marketplace_app_app_app_app_app_app_app_version_diff import diff_versions

def test_diff():
    r = diff_versions(
        {"name": "MyApp", "version": "1.0", "timeout": 30},
        {"name": "MyApp", "version": "2.0", "retries": 3},
    )
    assert len(r["added"]) == 1
    assert r["added"][0]["key"] == "retries"
    assert len(r["removed"]) == 1
    assert r["removed"][0]["key"] == "timeout"
    assert len(r["changed"]) == 1
    assert r["changed"][0]["key"] == "version"
    assert r["has_breaking"]
    assert r["total_changes"] == 3

def test_no_changes():
    r = diff_versions({"a": 1}, {"a": 1})
    assert r["total_changes"] == 0
    assert not r["has_breaking"]
