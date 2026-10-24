from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scylladb import fleet_scylladb_status
def test_scylla():
    r = fleet_scylladb_status([{"status": "UN", "ops_per_sec": 100000, "p99_ms": 2}])
    assert r["ops_per_sec"] == 100000
    assert r["healthy"]
