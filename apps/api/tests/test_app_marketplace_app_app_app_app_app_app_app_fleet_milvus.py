from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_milvus import fleet_milvus_status
def test_mv():
    r = fleet_milvus_status([{"healthy": True, "entities": 20000000, "search_qps": 3000}])
    assert r["entities"] == 20000000
    assert r["all_healthy"]
