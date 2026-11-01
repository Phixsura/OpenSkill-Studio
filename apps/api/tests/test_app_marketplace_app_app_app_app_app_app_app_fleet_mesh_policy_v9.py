from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_mesh_policy_v9 import fleet_mesh_policy_v9
def test_mp_v9():
    r = fleet_mesh_policy_v9([{"enforced": True, "action": "allow"}, {"enforced": True, "action": "deny"}])
    assert r["allow"] == 1
    assert r["deny"] == 1
    assert r["healthy"]
