from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_train_mon_v2 import fleet_ai_training_monitor_v2
def test_tmv2():
    r = fleet_ai_training_monitor_v2([{"active": True, "jobs": 200, "metrics": 5000, "alerts_24h": 10}])
    assert r["jobs"] == 200
    assert r["observing"]
