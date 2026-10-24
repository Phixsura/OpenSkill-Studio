from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_plan import forecast_capacity, recommend_scaling

def test_forecast():
    r = forecast_capacity(current_usage=60, growth_rate_pct=10, capacity=100, months_ahead=6)
    assert r["projections"][0]["month"] == 1
    assert r["exhaustion_month"] is not None

def test_no_exhaustion():
    r = forecast_capacity(current_usage=10, growth_rate_pct=5, capacity=100, months_ahead=6)
    assert r["exhaustion_month"] is None
    assert not r["action_needed"]

def test_recommend():
    r = recommend_scaling(85, 15)
    assert r["action"] == "scale_up_now"
    r2 = recommend_scaling(30, 5)
    assert r2["action"] == "monitor"
