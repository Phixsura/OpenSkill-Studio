from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_db_replication_v9 import fleet_db_replication_v9
def test_dbr_v9():
    r = fleet_db_replication_v9([{"lag_ms": 5}, {"lag_ms": 10}])
    assert r["synced"] == 2
    assert r["healthy"]
