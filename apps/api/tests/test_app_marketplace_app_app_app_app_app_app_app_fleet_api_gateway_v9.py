from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_gateway_v9 import fleet_api_gateway_v9
def test_gw_v9():
    r = fleet_api_gateway_v9([{"active": True, "rps": 10000, "throttled": False}])
    assert r["total_rps"] == 10000
    assert r["throttled"] == 0
    assert r["healthy"]
