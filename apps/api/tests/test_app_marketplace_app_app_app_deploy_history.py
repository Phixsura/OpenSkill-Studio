from app.services.app_marketplace_app_app_app_deploy_history import build_deploy_history

def test_history():
    deploys = [
        {"id": "d1", "version": "2.0.0", "environment": "production", "status": "success",
         "deployed_at": "2026-03-01", "deployer": "Alice", "commit": "abc123def", "duration_s": 120},
        {"id": "d2", "version": "1.5.0", "environment": "production", "status": "success",
         "deployed_at": "2026-02-01", "deployer": "Bob", "commit": "def456ghi", "duration_s": 90},
    ]
    r = build_deploy_history(deploys=deploys, current_version="2.0.0")
    assert r["total"] == 2
    assert r["deploys"][0]["is_current"]
    assert r["deploys"][1]["can_rollback"]
    assert r["success_rate"] == 100.0
