from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_status import aggregate_deploy_status, deploy_velocity

def test_aggregate():
    r = aggregate_deploy_status([
        {"env": "prod", "status": "success"},
        {"env": "prod", "status": "success"},
        {"env": "staging", "status": "failed"},
        {"env": "staging", "status": "in_progress"},
    ])
    assert r["total"] == 4
    assert not r["all_success"]
    assert r["by_env"]["prod"]["success"] == 2
    assert r["by_env"]["staging"]["failed"] == 1

def test_velocity():
    deploys = [{"status": "success"}] * 14 + [{"status": "failed"}] * 1
    r = deploy_velocity(deploys, days=7)
    assert r["per_day"] == 2.1
    assert r["success_rate"] == 93.3
