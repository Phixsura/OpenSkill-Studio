from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_flink import fleet_flink_status
def test_flink():
    r = fleet_flink_status([{"status": "RUNNING", "task_slots": 32, "checkpoint_ok": True}])
    assert r["task_slots"] == 32
    assert r["healthy"]
