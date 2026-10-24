from app.services.app_marketplace_app_app_app_app_app_app_app_ver_compare import compare_versions

def test_compare():
    r = compare_versions(
        {"version": "1.0", "features": ["auth", "webhooks", "basic_api"]},
        {"version": "2.0", "features": ["auth", "webhooks", "graphql", "sso"]})
    assert r["added"] == ["graphql", "sso"]
    assert r["removed"] == ["basic_api"]
    assert r["unchanged_count"] == 2
    assert r["breaking"]
    assert r["summary"] == "+2 -1 =2"
