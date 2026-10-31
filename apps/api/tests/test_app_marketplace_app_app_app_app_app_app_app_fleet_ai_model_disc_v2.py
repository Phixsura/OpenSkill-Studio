from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_disc_v2 import fleet_ai_model_discovery_v2
def test_mdv2():
    r = fleet_ai_model_discovery_v2([{"active": True, "searches_24h": 500000, "models": 5000, "recommendations": 2000000}])
    assert r["models"] == 5000
    assert r["intelligent"]
