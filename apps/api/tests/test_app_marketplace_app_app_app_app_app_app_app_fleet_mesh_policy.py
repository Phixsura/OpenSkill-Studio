from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_policy import fleet_mesh_policy
def test_policy():
    r = fleet_mesh_policy([{"has_access_policy": True, "default_deny": True}, {"has_access_policy": True, "default_deny": False}])
    assert r["with_policy"] == 2
    assert r["default_deny"] == 1
    assert not r["zero_trust"]
