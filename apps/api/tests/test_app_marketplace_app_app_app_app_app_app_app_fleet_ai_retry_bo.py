from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_retry_bo import fleet_ai_retry_backoff
def test_rb():
    r = fleet_ai_retry_backoff([{"active": True, "retries_24h": 100000, "max_backoff_s": 60, "jitter": True}])
    assert r["retries_24h"] == 100000
    assert r["smart"]
