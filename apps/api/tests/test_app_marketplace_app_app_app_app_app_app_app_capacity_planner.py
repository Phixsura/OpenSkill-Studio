from app.services.app_marketplace_app_app_app_app_app_app_app_capacity_planner import forecast_capacity, estimate_cost

def test_forecast():
    r = forecast_capacity(current_usage=500, growth_rate_pct=10,
                           capacity=1000, unit="GB", months_ahead=12)
    assert r["current_pct"] == 50.0
    assert r["exhaustion_month"] is not None
    assert r["exhaustion_month"] <= 12
    assert "URGENT" not in r["recommendation"]

def test_urgent():
    r = forecast_capacity(current_usage=900, growth_rate_pct=15,
                           capacity=1000, unit="GB", months_ahead=12)
    assert r["exhaustion_month"] == 1
    assert r["action_needed"]
    assert "URGENT" in r["recommendation"]

def test_cost():
    r = estimate_cost(current_cost=1000, growth_rate_pct=5, months=3)
    assert len(r["monthly_costs"]) == 3
    assert r["total_cost"] > 3000
