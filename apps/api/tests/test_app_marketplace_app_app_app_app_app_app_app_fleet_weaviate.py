from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_weaviate import fleet_weaviate_status
def test_wv():
    r = fleet_weaviate_status([{"healthy": True, "objects": 500000, "vectors": 500000}])
    assert r["objects"] == 500000
    assert r["all_healthy"]
