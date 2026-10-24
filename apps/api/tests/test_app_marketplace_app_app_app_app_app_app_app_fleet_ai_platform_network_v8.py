from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_network_v8 import fleet_ai_network_v8
def test_nv8():
    r = fleet_ai_network_v8([{"active": True, "tbps": 100, "latency_ms": 1, "regions": 30}])
    assert r["tbps"] == 100
    assert r["global"]
