from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_intent_cls import fleet_ai_intent_classifier
def test_ic():
    r = fleet_ai_intent_classifier([{"active": True, "classified_24h": 10000000, "intents": 200, "accuracy": 95}])
    assert r["intents"] == 200
    assert r["precise"]
