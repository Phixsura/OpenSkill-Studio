from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ner import fleet_ai_ner
def test_ner():
    r = fleet_ai_ner([{"active": True, "docs_24h": 1000000, "entities_found": 50000000, "entity_types": 20, "f1": 0.95}])
    assert r["f1"] == 0.95
    assert r["accurate"]
