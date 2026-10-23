from app.services.app_marketplace_app_developer_app_usage_alerts import check_usage_thresholds, build_usage_forecast, recommend_plan_upgrade

def test_no_alerts():
    alerts = check_usage_thresholds(usage={"api_calls": 500}, limits={"api_calls": 10000})
    assert len(alerts) == 0

def test_warning():
    alerts = check_usage_thresholds(usage={"api_calls": 8500}, limits={"api_calls": 10000})
    assert alerts[0]["level"] == "warning"

def test_critical():
    alerts = check_usage_thresholds(usage={"api_calls": 9800}, limits={"api_calls": 10000})
    assert alerts[0]["level"] == "critical"

def test_forecast_safe():
    r = build_usage_forecast(current=5000, daily_rate=100, limit=10000)
    assert not r["will_exceed"]

def test_forecast_danger():
    r = build_usage_forecast(current=9000, daily_rate=100, limit=10000)
    assert r["will_exceed"]
    assert r["days_until_limit"] == 10.0

def test_upgrade():
    alerts = [{"level": "critical", "resource": "api_calls"}]
    r = recommend_plan_upgrade(alerts=alerts, current_plan="free")
    assert r["recommended"] == "starter"

def test_no_upgrade():
    r = recommend_plan_upgrade(alerts=[], current_plan="free")
    assert r is None
