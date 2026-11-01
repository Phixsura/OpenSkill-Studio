from app.services.app_marketplace_app_app_app_app_app_app_app_usage_forecast import forecast_usage

def test_growing():
    r = forecast_usage([100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200])
    assert r["trend"] == "growing"
    assert r["projected_30d"] > 200

def test_stable():
    r = forecast_usage([100, 100, 100, 100, 100, 100, 100, 100, 100, 100])
    assert r["trend"] == "stable"
