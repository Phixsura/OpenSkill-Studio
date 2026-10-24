from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_etcd_v9 import fleet_cluster_etcd_v9
def test_etcd_v9():
    r = fleet_cluster_etcd_v9([{"etcd_healthy": True, "db_size_mb": 500, "leader_changes": 0}])
    assert r["etcd_healthy"] == 1
    assert r["healthy"]
