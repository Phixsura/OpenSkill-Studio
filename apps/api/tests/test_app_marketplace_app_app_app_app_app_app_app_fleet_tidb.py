from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_tidb import fleet_tidb_status
def test_tidb():
    r = fleet_tidb_status([{"healthy": True, "tikv_stores": 9, "qps": 100000}])
    assert r["tikv_stores"] == 9
    assert r["all_healthy"]
