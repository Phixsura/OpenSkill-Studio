from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_etcd import fleet_etcd_health
def test_etcd():
    r = fleet_etcd_health([{"healthy": True, "key_count": 10000, "db_size_mb": 100}, {"healthy": True, "key_count": 10000, "db_size_mb": 100}, {"healthy": False, "key_count": 10000, "db_size_mb": 100}])
    assert r["healthy"] == 2
    assert r["quorum"]
    assert r["total_keys"] == 30000
