from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mlflow import fleet_mlflow_status
def test_mlf():
    r = fleet_mlflow_status([{"running": True, "experiments": 100, "runs_24h": 5000, "registered_models": 50}])
    assert r["experiments"] == 100
    assert r["registered_models"] == 50
