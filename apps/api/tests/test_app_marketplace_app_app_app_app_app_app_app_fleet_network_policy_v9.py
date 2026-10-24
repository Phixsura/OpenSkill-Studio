from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_network_policy_v9 import fleet_network_policy_v9
def test_netpol_v9():
    r = fleet_network_policy_v9([{"enforced": True, "violations": 0, "segment": "prod"}])
    assert r["enforced"] == 1
    assert r["violations"] == 0
    assert r["healthy"]
