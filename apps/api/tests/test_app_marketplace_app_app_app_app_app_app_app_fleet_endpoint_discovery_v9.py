from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_endpoint_discovery_v9 import fleet_endpoint_discovery_v9
def test_ed2_v9():
    r = fleet_endpoint_discovery_v9([{"auto_discovered": True, "registered": True, "stale": False}])
    assert r["auto_discovered"] == 1
    assert r["healthy"]
