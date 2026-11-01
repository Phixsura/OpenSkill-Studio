from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_migration import fleet_migration_status
def test_migration():
    r = fleet_migration_status([{"pending_migrations": 0}, {"pending_migrations": 3}])
    assert r["current"] == 1
    assert r["total_pending"] == 3
    assert not r["all_current"]
