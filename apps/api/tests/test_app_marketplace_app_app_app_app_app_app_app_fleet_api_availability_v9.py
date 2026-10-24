from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_availability_v9 import fleet_api_availability_v9
def test_aav2_v9():
    r = fleet_api_availability_v9([{"available": True, "uptime_pct": 99.999, "failovers_30d": 0}])
    assert r["available"] == 1
    assert r["healthy"]
