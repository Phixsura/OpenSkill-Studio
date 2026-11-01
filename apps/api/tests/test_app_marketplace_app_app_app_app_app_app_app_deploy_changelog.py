from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_changelog import build_deploy_changelog

def test_changelog():
    r = build_deploy_changelog([
        {"version": "2.1.0", "env": "prod", "deployer": "alice",
         "changes": [{"type": "feat", "msg": "dark mode"}, {"type": "fix", "msg": "login bug"}]},
        {"version": "2.0.1", "changes": [{"type": "fix", "msg": "typo"}]},
    ])
    assert r["total_deployments"] == 2
    assert r["total_features"] == 1
    assert r["total_fixes"] == 2
    assert r["entries"][0]["version"] == "2.1.0"
