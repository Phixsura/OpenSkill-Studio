from app.services.app_marketplace_app_changelog_diff_viewer import compute_version_diff

def test_diff():
    d = compute_version_diff(
        old_version={"permissions": ["read", "write"], "endpoints": ["/users", "/apps"], "config_schema": {"url": {}}},
        new_version={"permissions": ["read", "admin"], "endpoints": ["/users", "/orgs"], "config_schema": {"url": {}, "timeout": {}}})
    assert d["permissions"]["added"] == ["admin"]
    assert d["permissions"]["removed"] == ["write"]
    assert d["endpoints"]["added"] == ["/orgs"]
    assert d["has_breaking"]
    assert d["total_changes"] > 0

def test_no_changes():
    d = compute_version_diff(old_version={"permissions": ["read"]}, new_version={"permissions": ["read"]})
    assert not d["has_breaking"]
    assert d["total_changes"] == 0
