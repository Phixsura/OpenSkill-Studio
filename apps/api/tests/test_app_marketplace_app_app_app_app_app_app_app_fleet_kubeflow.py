from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_kubeflow import fleet_kubeflow_status
def test_kf():
    r = fleet_kubeflow_status([{"healthy": True, "pipelines": 50, "notebooks": 20, "experiments": 100}])
    assert r["pipelines"] == 50
    assert r["experiments"] == 100
