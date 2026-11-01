from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_history import build_deploy_history

def test_history():
    r = build_deploy_history([
        {"version": "2.1.0", "environment": "production", "status": "success", "deployer": "alice", "duration_sec": 120},
        {"version": "2.0.5", "environment": "staging", "status": "success", "deployer": "bob", "duration_sec": 90},
        {"version": "2.0.4", "environment": "production", "status": "failed", "deployer": "alice", "duration_sec": 45},
    ])
    assert r["total"] == 3
    assert r["success_count"] == 2
    assert r["success_rate"] == 67
