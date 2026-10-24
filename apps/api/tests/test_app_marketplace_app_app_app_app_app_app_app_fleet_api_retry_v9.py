from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_retry_v9 import fleet_api_retry_v9
def test_aretry_v9():
    r = fleet_api_retry_v9([{"retries_today": 500, "succeeded_after_retry": 490, "retries_exhausted": 0}])
    assert r["succeeded_after_retry"] == 490
    assert r["healthy"]
