from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_ner import fleet_ai_ner
def test_ner():
    r = fleet_ai_ner([{"active": True, "docs_24h": 1000000, "entities_24h": 20000000}])
    assert r["entities_24h"] == 20000000
    assert r["productive"]
