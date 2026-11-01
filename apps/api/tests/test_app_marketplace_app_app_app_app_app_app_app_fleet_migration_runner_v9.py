from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_migration_runner_v9 import fleet_migration_runner_v9
def test_mig_v9():
    r = fleet_migration_runner_v9([{"applied": True}, {"applied": True}])
    assert r["pending"] == 0
    assert r["healthy"]
