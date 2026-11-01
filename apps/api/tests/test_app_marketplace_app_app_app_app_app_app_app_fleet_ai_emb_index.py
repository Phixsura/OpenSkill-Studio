from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_emb_index import fleet_ai_embedding_index
def test_ei():
    r = fleet_ai_embedding_index([{"active": True, "vectors": 100000000, "dims": 1536, "searches_24h": 10000000, "p99_ms": 15}])
    assert r["vectors"] == 100000000
    assert r["fast"]
