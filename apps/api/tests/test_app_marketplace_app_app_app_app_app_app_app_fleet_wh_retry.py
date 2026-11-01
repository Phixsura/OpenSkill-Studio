from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_wh_retry import fleet_webhook_retry
def test_retry():
    r = fleet_webhook_retry([{"retries": 100, "recovered_after_retry": 80, "retries_exhausted": 20}])
    assert r["recovered"] == 80
    assert r["recovery_rate"] == 80.0
