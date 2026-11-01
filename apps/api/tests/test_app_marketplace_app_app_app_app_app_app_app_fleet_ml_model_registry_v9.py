from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ml_model_registry_v9 import fleet_ml_model_registry_v9
def test_ml_v9():
    r = fleet_ml_model_registry_v9([{"deployed": True, "versions": 5, "accuracy": 0.95}])
    assert r["deployed"] == 1
    assert r["avg_accuracy"] == 0.95
    assert r["healthy"]
