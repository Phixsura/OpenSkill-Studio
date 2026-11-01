from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_discovery_v9 import fleet_api_discovery_v9
def test_adisc_v9():
    r = fleet_api_discovery_v9([{"endpoints_found": 200, "registered": 200, "stale": 0}])
    assert r["discovered"] == 200
    assert r["healthy"]
