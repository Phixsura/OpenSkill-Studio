from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cluster_security_v9 import fleet_cluster_security_v9
def test_csec_v9():
    r = fleet_cluster_security_v9([{"rbac": True, "pod_security": True, "network_policies": True, "security_score": 95}])
    assert r["rbac"] == 1
    assert r["healthy"]
