from app.services.app_marketplace_app_app_app_app_app_app_app_ep_traffic_forecast import forecast_endpoint_traffic

def test_growing():
    r = forecast_endpoint_traffic("/api/users", [100, 120, 140, 160, 180, 200])
    assert r["trend"] == "growing"
    assert r["forecast"][-1]["projected_rps"] > 200

def test_stable():
    r = forecast_endpoint_traffic("/api/health", [100, 101, 99, 100, 100, 100])
    assert r["trend"] == "stable"
