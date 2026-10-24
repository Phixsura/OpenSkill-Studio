from app.services.app_marketplace_app_app_app_app_app_app_app_deploy_freq import calculate_frequency, lead_time

def test_on_demand():
    deploys = [{"env": "prod"} for _ in range(60)]
    r = calculate_frequency(deploys, period_days=30)
    assert r["frequency"] == "on_demand"
    assert r["deploys_per_day"] == 2.0

def test_weekly():
    r = calculate_frequency([{"env": "prod"}] * 4, period_days=30)
    assert r["frequency"] == "weekly"

def test_lead_time():
    r = lead_time([{"lead_time_hours": 2}, {"lead_time_hours": 4}, {"lead_time_hours": 6}])
    assert r["avg_hours"] == 4.0
    assert r["min_hours"] == 2
