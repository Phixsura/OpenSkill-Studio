from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_model_ep_v3 import fleet_ai_model_endpoint_v3
def test_mev3():
    r = fleet_ai_model_endpoint_v3([{"active": True, "rps": 1000000, "p50_ms": 15, "p99_ms": 50}])
    assert r["rps"] == 1000000
    assert r["performant"]
