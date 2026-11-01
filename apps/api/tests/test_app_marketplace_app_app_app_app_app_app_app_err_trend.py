from app.services.app_marketplace_app_app_app_app_app_app_app_err_trend import error_trend

def test_worsening():
    r = error_trend([{"error_rate": 0.1}, {"error_rate": 0.2}, {"error_rate": 2.0}, {"error_rate": 3.0}])
    assert r["trend"] == "worsening"

def test_stable():
    r = error_trend([{"error_rate": 0.1}, {"error_rate": 0.12}, {"error_rate": 0.1}, {"error_rate": 0.11}])
    assert r["trend"] == "stable"
