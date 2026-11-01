from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_db_migration_tracker_v9 import fleet_db_migration_tracker_v9
def test_dmt_v9():
    r = fleet_db_migration_tracker_v9([{"migration_synced": True, "pending_migrations": 0, "applied": 50}])
    assert r["pending_migrations"] == 0
    assert r["healthy"]
