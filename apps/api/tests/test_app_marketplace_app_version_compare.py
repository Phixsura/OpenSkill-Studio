from app.services.app_marketplace_app_version_compare import compare_versions

def test_compare():
    r = compare_versions({"version": "1.0", "permissions": ["read:cohorts"]}, {"version": "2.0", "permissions": ["read:cohorts", "write:cohorts"]})
    assert r["permissions_added"] == ["write:cohorts"]
    assert r["breaking"] is False
