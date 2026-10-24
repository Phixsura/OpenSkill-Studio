from app.services.app_marketplace_app_app_app_app_app_app_app_cost_svc_trend import cost_trend
def test_increasing():
    r = cost_trend([{"cost": 100}, {"cost": 150}, {"cost": 200}])
    assert r["trend"] == "increasing"
