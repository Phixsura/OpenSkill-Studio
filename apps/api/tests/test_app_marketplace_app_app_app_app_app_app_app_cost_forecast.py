from app.services.app_marketplace_app_app_app_app_app_app_app_cost_forecast import forecast_costs, identify_savings

def test_forecast():
    r = forecast_costs([1000, 1100, 1200, 1300], months_ahead=3)
    assert r["trend"] == "increasing"
    assert r["avg_monthly_growth"] == 100.0
    assert len(r["forecast"]) == 3
    assert r["forecast"][0]["projected_cost"] == 1400.0

def test_savings():
    r = identify_savings({"compute": 5000, "storage": 1000, "network": 500}, threshold_pct=20)
    assert len(r) == 1
    assert r[0]["service"] == "compute"
