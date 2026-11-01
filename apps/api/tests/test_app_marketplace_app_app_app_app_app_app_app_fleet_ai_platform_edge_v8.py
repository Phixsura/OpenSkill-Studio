from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_platform_edge_v8 import fleet_ai_edge_v8
def test_ev8():
    r = fleet_ai_edge_v8([{"active": True, "locations": 200, "requests_24h": 10000000000, "p50_ms": 2}])
    assert r["locations"] == 200
    assert r["ultra_low"]
