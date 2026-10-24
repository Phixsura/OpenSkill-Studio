from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_intent import fleet_ai_intent
def test_int():
    r = fleet_ai_intent([{"active": True, "classifications_24h": 5000000, "intents_defined": 200}])
    assert r["classifications_24h"] == 5000000
    assert r["all_active"]
