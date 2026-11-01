from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_notification_hub_v9 import fleet_notification_hub_v9
def test_nh_v9():
    r = fleet_notification_hub_v9([{"sent": 10000, "failed": 0, "type": "email"}, {"sent": 5000, "failed": 0, "type": "slack"}])
    assert r["sent"] == 15000
    assert r["channel_types"] == 2
    assert r["healthy"]
