from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_request_logging_v9 import fleet_api_request_logging_v9
def test_arlg_v9():
    r = fleet_api_request_logging_v9([{"structured": True, "entries_today": 1000000, "size_gb": 50}])
    assert r["entries_today"] == 1000000
    assert r["healthy"]
