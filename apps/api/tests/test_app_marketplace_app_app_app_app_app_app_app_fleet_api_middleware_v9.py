from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_middleware_v9 import fleet_api_middleware_v9
def test_amw_v9():
    r = fleet_api_middleware_v9([{"active": True, "type": "auth", "overhead_ms": 1.5}])
    assert r["auth"] == 1
    assert r["healthy"]
