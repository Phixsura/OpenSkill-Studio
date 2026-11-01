from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_k8s_rbac_v9 import fleet_k8s_rbac_v9
def test_krbac_v9():
    r = fleet_k8s_rbac_v9([{"type": "ClusterRole", "bindings": 5, "over_privileged": False}])
    assert r["cluster_roles"] == 1
    assert r["healthy"]
