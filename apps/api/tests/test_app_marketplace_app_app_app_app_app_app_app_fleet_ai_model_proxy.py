from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_proxy import fleet_ai_model_proxy
def test_mp():
    r = fleet_ai_model_proxy([{"active": True, "requests_24h": 100000000, "models": 30, "overhead_ms": 2}])
    assert r["models"] == 30
    assert r["transparent"]
