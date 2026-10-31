from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_relay_v9 import fleet_webhook_relay_v9
def test_wh_v9():
    r = fleet_webhook_relay_v9([{"delivered": 10000, "failed": 0, "retries": 5}])
    assert r["delivered"] == 10000
    assert r["healthy"]
