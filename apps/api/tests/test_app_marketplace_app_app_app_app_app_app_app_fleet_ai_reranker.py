from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_reranker import fleet_ai_reranker
def test_rr():
    r = fleet_ai_reranker([{"active": True, "queries_24h": 5000000, "ndcg_boost": 0.15, "latency_ms": 20}])
    assert r["ndcg_boost"] == 0.15
    assert r["improving"]
