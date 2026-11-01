from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scheduled_task_v9 import fleet_scheduled_task_v9
def test_st_v9():
    r = fleet_scheduled_task_v9([{"on_time": True, "drift_sec": 2}])
    assert r["on_time"] == 1
    assert r["healthy"]
