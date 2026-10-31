from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cron_scheduler_v9 import fleet_cron_scheduler_v9
def test_cron_v9():
    r = fleet_cron_scheduler_v9([{"status": "idle", "last_result": "success", "due_in_min": 10}])
    assert r["failed_last_run"] == 0
    assert r["healthy"]
