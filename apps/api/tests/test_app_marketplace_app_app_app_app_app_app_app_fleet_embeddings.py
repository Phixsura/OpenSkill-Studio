from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_embeddings import fleet_embeddings_status
def test_emb():
    r = fleet_embeddings_status([{"active": True, "embeddings_24h": 10000000, "dimensions": 1536}])
    assert r["embeddings_24h"] == 10000000
    assert r["max_dimensions"] == 1536
