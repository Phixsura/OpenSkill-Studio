from app.services.app_marketplace_revenue_forecast import forecast_revenue

def test_forecast():
    r = forecast_revenue(monthly_revenues=[1000, 1100, 1210], months_ahead=3)
    assert r["avg_growth_rate"] == 10.0
    assert len(r["projections"]) == 3
    assert r["projections"][0]["projected_revenue"] > 1210
    assert r["projections"][0]["confidence"] >= 0.5

def test_too_few():
    r = forecast_revenue(monthly_revenues=[500])
    assert "error" in r

def test_declining():
    r = forecast_revenue(monthly_revenues=[1000, 900, 810])
    assert r["avg_growth_rate"] < 0
    assert r["projections"][0]["projected_revenue"] < 810
