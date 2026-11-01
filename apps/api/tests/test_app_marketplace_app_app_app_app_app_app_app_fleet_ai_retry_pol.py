from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_retry_pol import fleet_ai_retry_policy
def test_rp():
    r = fleet_ai_retry_policy([{"active": True, "retries_24h": 50000, "success_retries": 48000, "max_attempts": 3}])
    assert r["retries_24h"] == 50000
    assert r["resilient"]
