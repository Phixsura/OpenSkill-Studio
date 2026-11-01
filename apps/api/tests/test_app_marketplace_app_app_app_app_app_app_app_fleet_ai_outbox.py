from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_outbox import fleet_ai_outbox
def test_ob():
    r = fleet_ai_outbox([{"active": True, "messages_24h": 50000000, "pending": 10, "published": 49999990}])
    assert r["published"] == 49999990
    assert r["caught_up"]
