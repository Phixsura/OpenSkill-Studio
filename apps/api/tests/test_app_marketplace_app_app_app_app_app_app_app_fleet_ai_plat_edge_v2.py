from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_plat_edge_v2 import fleet_ai_edge_v2
def test_ev2():
    r = fleet_ai_edge_v2([{"active": True, "locations": 50, "requests_24h": 1000000000, "p50_ms": 5}])
    assert r["locations"] == 50
    assert r["global"]
