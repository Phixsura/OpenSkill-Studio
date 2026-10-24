from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_haystack import fleet_haystack_status
def test_hs():
    r = fleet_haystack_status([{"active": True, "nodes": 15, "queries_24h": 200000}])
    assert r["nodes"] == 15
    assert r["all_active"]
