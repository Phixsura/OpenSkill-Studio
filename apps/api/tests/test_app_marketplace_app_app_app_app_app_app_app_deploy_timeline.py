from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_timeline import build_deploy_timeline

def test_timeline():
    r = build_deploy_timeline([
        {"environment": "production", "status": "success", "duration_sec": 120},
        {"environment": "staging", "status": "success", "duration_sec": 90},
        {"environment": "production", "status": "failed", "duration_sec": 30},
    ])
    assert r["total"] == 3
    assert r["by_environment"]["production"] == 2
    assert r["success_rate"] == 67
    assert r["avg_duration_sec"] == 80
