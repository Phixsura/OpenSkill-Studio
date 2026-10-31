from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_pubsub import fleet_pubsub_status
def test_ps():
    r = fleet_pubsub_status([{"messages_24h": 5000000, "subscriptions": 20, "backlog_messages": 500}])
    assert r["messages_24h"] == 5000000
    assert r["healthy"]
