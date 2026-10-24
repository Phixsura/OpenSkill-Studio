from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_embeddings import fleet_ai_embeddings
def test_emb():
    r = fleet_ai_embeddings([{"active": True, "vectors_24h": 5000000, "dimensions": 1536}])
    assert r["vectors_24h"] == 5000000
    assert r["max_dimensions"] == 1536
    assert r["healthy"]
