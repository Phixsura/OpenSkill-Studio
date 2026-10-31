from app.services.app_marketplace_app_app_app_app_app_app_app_growth_tracker import track_growth, growth_forecast

def test_growth():
    r = track_growth([
        {"users": 1000, "apps": 50, "revenue": 5000, "api_calls": 100000},
        {"users": 1500, "apps": 75, "revenue": 7500, "api_calls": 200000},
    ])
    assert r["overall"] == "growing"
    assert r["metrics"]["users"]["growth_pct"] == 50.0

def test_forecast():
    r = growth_forecast(1000, 10, 3)
    assert r["projections"][0]["projected"] == 1100.0
    assert r["final"] > 1000
