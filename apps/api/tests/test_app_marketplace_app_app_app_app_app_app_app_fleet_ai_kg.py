from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_kg import fleet_ai_knowledge_graph
def test_kg():
    r = fleet_ai_knowledge_graph([{"active": True, "entities": 1000000, "relations": 5000000, "queries_24h": 200000}])
    assert r["entities"] == 1000000
    assert r["connected"]
