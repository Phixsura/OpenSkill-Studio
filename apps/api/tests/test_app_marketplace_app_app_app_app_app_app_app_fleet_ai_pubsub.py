from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_pubsub import fleet_ai_pubsub
def test_ps():
    r = fleet_ai_pubsub([{"active": True, "topics": 200, "subscriptions": 1000, "messages_24h": 500000000}])
    assert r["topics"] == 200
    assert r["connected"]
