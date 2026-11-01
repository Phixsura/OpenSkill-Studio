from app.services.app_marketplace_app_app_app_app_app_app_app_budget_forecast import forecast_budget, recommend_action

def test_forecast():
    r = forecast_budget(budget_total=1000, consumed=500, daily_burn=50, days_in_period=30)
    assert r["remaining"] == 500
    assert r["days_until_exhaustion"] == 10
    assert r["will_exhaust"]

def test_safe():
    r = forecast_budget(budget_total=1000, consumed=100, daily_burn=10, days_in_period=30)
    assert not r["will_exhaust"]

def test_recommend_critical():
    forecast = {"days_until_exhaustion": 2, "will_exhaust": True}
    r = recommend_action(forecast)
    assert r["action"] == "freeze_deploys"
    assert r["urgency"] == "critical"
