from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_migration_v9 import fleet_cloud_migration_v9
def test_cmig_v9():
    r = fleet_cloud_migration_v9([{"migrated": True, "status": "done"}])
    assert r["migrated"] == 1
    assert r["healthy"]
