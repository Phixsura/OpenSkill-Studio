from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mig_tracker import fleet_migration_tracker
def test_mig():
    r = fleet_migration_tracker([{"status": "completed"}, {"status": "in_progress"}, {"status": "blocked"}])
    assert r["completed"] == 1
    assert r["blocked"] == 1
    assert not r["all_done"]
