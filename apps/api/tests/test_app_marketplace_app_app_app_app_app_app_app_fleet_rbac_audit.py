from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_rbac_audit import fleet_rbac_audit
def test_rbac():
    r = fleet_rbac_audit([{"cluster_admin": False}, {"cluster_admin": True}, {"cluster_admin": False, "has_resource_limits": False}])
    assert r["overprivileged"] == 1
    assert r["no_limits"] == 1
    assert not r["compliant"]
