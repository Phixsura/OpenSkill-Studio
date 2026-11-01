from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_train_sched import fleet_ai_training_scheduler
def test_ts():
    r = fleet_ai_training_scheduler([{"active": True, "queued": 20, "running": 50, "completed_24h": 200, "avg_wait_min": 5}])
    assert r["running"] == 50
    assert r["fast"]
