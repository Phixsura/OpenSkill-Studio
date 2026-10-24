from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_chroma import fleet_chroma_status
def test_chroma():
    r = fleet_chroma_status([{"documents": 100000, "embeddings": 100000}])
    assert r["documents"] == 100000
    assert r["synced"]
