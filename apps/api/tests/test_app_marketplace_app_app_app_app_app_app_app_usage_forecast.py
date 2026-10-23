from app.services.app_marketplace_app_app_app_app_app_app_app_usage_forecast import forecast_usage

def test_forecast():
    data = [{"value": 100}, {"value": 120}, {"value": 140}, {"value": 160}, {"value": 180}]
    r = forecast_usage(data, months_ahead=3)
    assert r["trend"] == "growing"
    assert r["slope"] == 20.0
    assert len(r["predictions"]) == 3
    assert r["predictions"][0]["predicted"] > 180

def test_flat():
    data = [{"value": 50}, {"value": 50}, {"value": 50}]
    r = forecast_usage(data)
    assert r["trend"] == "flat"
    assert r["slope"] == 0
