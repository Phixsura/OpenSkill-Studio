from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_velocity import calculate_velocity

def test_velocity():
    deploys = [
        {"team": "platform", "environment": "production", "status": "success"}
    ] * 30 + [{"team": "frontend", "environment": "staging", "status": "success"}] * 15
    r = calculate_velocity(deploys, 30)
    assert r["total"] == 45
    assert r["per_day"] == 1.5
    assert r["fastest_team"] == "platform"
    assert r["success_rate"] == 100
