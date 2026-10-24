from app.services.app_marketplace_app_app_deploy_status import build_deploy_status

def test_deploy_status():
    deps = [
        {"environment": "production", "version": "2.0.0", "status": "success", "deployed_at": "2026-01-03", "deployer": "Alice", "commit": "abc123def"},
        {"environment": "staging", "version": "2.1.0", "status": "success", "deployed_at": "2026-01-04", "deployer": "Bob"},
        {"environment": "development", "version": "2.1.0", "status": "success", "deployed_at": "2026-01-04"},
    ]
    r = build_deploy_status(deployments=deps)
    assert r["env_count"] == 3
    assert not r["versions_in_sync"]  # prod is 2.0.0, others 2.1.0
    assert r["environments"][0]["icon"] == "🟢"

def test_in_sync():
    deps = [
        {"environment": "staging", "version": "1.0.0", "deployed_at": "2026-01-01"},
        {"environment": "production", "version": "1.0.0", "deployed_at": "2026-01-01"},
    ]
    r = build_deploy_status(deployments=deps)
    assert r["versions_in_sync"]
