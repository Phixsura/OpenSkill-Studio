from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k8s_operator_v9 import fleet_k8s_operator_v9
def test_k8s_v9():
    r = fleet_k8s_operator_v9([{"status": "running", "reconciles_per_min": 100, "errors": 0}])
    assert r["running"] == 1
    assert r["healthy"]
