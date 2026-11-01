from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_migration_guide_v9 import fleet_api_migration_guide_v9
def test_amg_v9():
    r = fleet_api_migration_guide_v9([{"completed": True, "in_progress": False, "consumers_migrated": 50}])
    assert r["completed"] == 1
    assert r["healthy"]
