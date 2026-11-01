from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_webhook_validator_v9 import fleet_webhook_validator_v9
def test_wv_v9():
    r = fleet_webhook_validator_v9([{"validated": 10000, "rejected": 50, "replay_blocked": 5}])
    assert r["validated"] == 10000
    assert r["healthy"]
