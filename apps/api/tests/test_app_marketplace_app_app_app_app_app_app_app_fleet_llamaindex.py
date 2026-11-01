from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_llamaindex import fleet_llamaindex_status
def test_li():
    r = fleet_llamaindex_status([{"active": True, "indexes": 10, "queries_24h": 200000}])
    assert r["indexes"] == 10
    assert r["all_active"]
