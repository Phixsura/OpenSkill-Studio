from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_postgres import fleet_postgres_status
def test_pg():
    r = fleet_postgres_status([{"role": "primary", "active_connections": 50}, {"role": "replica", "replication_lag_mb": 10, "active_connections": 30}])
    assert r["primary"] == 1
    assert r["max_replication_lag_mb"] == 10
    assert r["healthy"]
