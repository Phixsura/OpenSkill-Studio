from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_retry_policy_v9 import fleet_retry_policy_v9
def test_rp_v9():
    r = fleet_retry_policy_v9([{"strategy": "exponential", "retries_today": 100}])
    assert r["exponential"] == 1
    assert r["healthy"]
