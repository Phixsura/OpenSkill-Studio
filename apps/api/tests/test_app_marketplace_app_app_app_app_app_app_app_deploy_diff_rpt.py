from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_diff_rpt import compare_deployments

def test_compare():
    r = compare_deployments(
        {"services": [{"name": "api", "version": "1.0"}, {"name": "old", "version": "1.0"}]},
        {"services": [{"name": "api", "version": "2.0"}, {"name": "new", "version": "1.0"}]})
    assert "new" in r["added"]
    assert "old" in r["removed"]
    assert r["upgraded"][0]["service"] == "api"
    assert r["total_changes"] == 3
    assert not r["has_rollbacks"]
