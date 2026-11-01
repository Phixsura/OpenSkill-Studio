from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_backup_v9 import fleet_cluster_backup_v9
def test_cb2_v9():
    r = fleet_cluster_backup_v9([{"status": "success", "size_gb": 5, "age_hours": 2}])
    assert r["successful"] == 1
    assert r["healthy"]
