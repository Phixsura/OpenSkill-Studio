from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_servicebus import fleet_servicebus_status
def test_sb():
    r = fleet_servicebus_status([{"status": "Active", "messages_24h": 1000000, "dlq_count": 5}])
    assert r["messages_24h"] == 1000000
    assert not r["healthy"]
