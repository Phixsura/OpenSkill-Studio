from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_dist_train_v2 import fleet_ai_distributed_training_v2
def test_dtv2():
    r = fleet_ai_distributed_training_v2([{"active": True, "nodes": 100, "gpus": 800, "efficiency_pct": 92}])
    assert r["gpus"] == 800
    assert r["scalable"]
