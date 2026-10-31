from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_proxy_v9 import fleet_api_proxy_v9
def test_aprox_v9():
    r = fleet_api_proxy_v9([{"active": True, "rps": 50000, "backends": 5, "errors_today": 0}])
    assert r["total_rps"] == 50000
    assert r["healthy"]
