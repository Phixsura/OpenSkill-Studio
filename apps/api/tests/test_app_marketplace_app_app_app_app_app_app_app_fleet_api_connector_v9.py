from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_connector_v9 import fleet_api_connector_v9
def test_acon2_v9():
    r = fleet_api_connector_v9([{"connected": True, "error": False, "calls_today": 10000}])
    assert r["connected"] == 1
    assert r["healthy"]
