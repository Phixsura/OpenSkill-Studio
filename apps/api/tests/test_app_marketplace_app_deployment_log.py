from app.services.app_marketplace_app_deployment_log import create_deployment_entry, get_deployment_stats

def test_create():
    r = create_deployment_entry(app_id="a1", version="2.0", environment="production",
        deployed_by="alice", strategy="canary")
    assert r["deployment_id"].startswith("deploy_")
    assert r["status"] == "in_progress"
    assert r["strategy"] == "canary"

def test_stats():
    deploys = [
        {"status": "success", "environment": "production", "duration_sec": 120},
        {"status": "success", "environment": "staging", "duration_sec": 60},
        {"status": "failed", "environment": "production", "duration_sec": 30},
    ]
    r = get_deployment_stats(deployments=deploys)
    assert r["success_rate"] == 66.7
    assert r["avg_duration_sec"] == 70.0
    assert r["by_environment"]["production"] == 2
