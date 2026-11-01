from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_acl_v9 import fleet_network_acl_v9
def test_nacl_v9():
    r = fleet_network_acl_v9([{"active": True, "allow_rules": 10, "deny_rules": 5}])
    assert r["allow_rules"] == 10
    assert r["healthy"]
