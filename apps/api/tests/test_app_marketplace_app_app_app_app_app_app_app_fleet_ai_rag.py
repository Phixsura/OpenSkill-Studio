from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_rag import fleet_ai_rag_pipeline
def test_rag():
    r = fleet_ai_rag_pipeline([{"active": True, "queries_24h": 500000, "docs_indexed": 10000000, "relevance": 0.95}])
    assert r["docs_indexed"] == 10000000
    assert r["quality"]
