from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_sem_search import fleet_ai_semantic_search
def test_ss():
    r = fleet_ai_semantic_search([{"active": True, "queries_24h": 2000000, "docs_indexed": 100000000, "mrr": 0.92}])
    assert r["mrr"] == 0.92
    assert r["accurate"]
