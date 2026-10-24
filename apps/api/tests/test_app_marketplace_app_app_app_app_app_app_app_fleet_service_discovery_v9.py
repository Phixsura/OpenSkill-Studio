from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_discovery_v9 import fleet_service_discovery_v9
def test_sd_v9():
    r = fleet_service_discovery_v9([{"registered": True, "health": "healthy", "endpoints": 3}])
    assert r["total_endpoints"] == 3
    assert r["healthy"]
