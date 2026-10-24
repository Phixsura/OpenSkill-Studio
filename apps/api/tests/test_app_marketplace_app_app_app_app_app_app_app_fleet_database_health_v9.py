from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_database_health_v9 import fleet_database_health_v9
def test_dbh_v9():
    r = fleet_database_health_v9([{"healthy": True, "active_connections": 100, "queries_per_sec": 5000, "replication_lag_ms": 5}])
    assert r["qps"] == 5000
    assert r["all_healthy"]
