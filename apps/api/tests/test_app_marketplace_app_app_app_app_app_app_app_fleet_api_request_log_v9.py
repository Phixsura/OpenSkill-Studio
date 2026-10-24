from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_request_log_v9 import fleet_api_request_log_v9
def test_arl_v9():
    r = fleet_api_request_log_v9([{"enabled": True, "entries_per_sec": 10000, "storage_gb": 100}])
    assert r["entries_per_sec"] == 10000
    assert r["healthy"]
