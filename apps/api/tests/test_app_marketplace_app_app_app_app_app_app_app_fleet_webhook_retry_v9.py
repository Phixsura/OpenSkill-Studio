from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_retry_v9 import fleet_webhook_retry_v9
def test_wr2_v9():
    r = fleet_webhook_retry_v9([{"pending": 10, "retrying": 2, "dead_letter": 0}])
    assert r["dead_letter"] == 0
    assert r["healthy"]
