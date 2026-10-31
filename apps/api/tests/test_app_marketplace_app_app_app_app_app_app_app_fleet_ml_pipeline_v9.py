from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ml_pipeline_v9 import fleet_ml_pipeline_v9
def test_mlp_v9():
    r = fleet_ml_pipeline_v9([{"phase": "training", "gpu_hours": 100}, {"phase": "inference", "gpu_hours": 50}])
    assert r["training"] == 1
    assert r["gpu_hours"] == 150
    assert r["healthy"]
