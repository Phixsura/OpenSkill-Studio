from app.services.app_marketplace_app_plan_usage_forecast import forecast_limit_breach, recommend_plan_upgrade

def test_forecast():
    r = forecast_limit_breach(current_usage=7000, limit=10000, daily_growth=200)
    assert r["days_until_breach"] == 15
    assert r["urgency"] == "ok"

def test_critical():
    r = forecast_limit_breach(current_usage=9500, limit=10000, daily_growth=200)
    assert r["urgency"] == "critical"

def test_breached():
    r = forecast_limit_breach(current_usage=11000, limit=10000, daily_growth=100)
    assert r["breached"]

def test_unlimited():
    r = forecast_limit_breach(current_usage=5000, limit=0, daily_growth=100)
    assert r["unlimited"]

def test_recommend():
    plans = [
        {"name": "starter", "price": 29, "limits": {"api_calls": 50000}},
        {"name": "pro", "price": 99, "limits": {"api_calls": 500000}},
    ]
    r = recommend_plan_upgrade(usage={"api_calls": 30000}, plans=plans)
    assert r["recommended"]["name"] == "starter"
