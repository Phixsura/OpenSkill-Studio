from app.services.app_marketplace_app_app_app_app_app_app_app_health_trend import calculate_health_trend, health_forecast

def test_improving():
    r = calculate_health_trend([80, 82, 85, 88, 90, 92, 95])
    assert r["trend"] == "improving"
    assert r["delta"] > 0

def test_stable():
    r = calculate_health_trend([90, 91, 89, 90, 91, 90, 89])
    assert r["trend"] == "stable"

def test_forecast():
    r = health_forecast([80, 85, 90])
    assert len(r["forecast"]) == 3
    assert r["forecast"][0]["projected"] > 90
