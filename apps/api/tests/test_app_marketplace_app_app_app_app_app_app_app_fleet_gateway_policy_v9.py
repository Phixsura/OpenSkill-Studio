from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gateway_policy_v9 import fleet_gateway_policy_v9
def test_gp_v9():
    r = fleet_gateway_policy_v9([{"enforced": True, "type": "auth"}, {"enforced": True, "type": "cors"}])
    assert r["enforced"] == 2
    assert r["healthy"]
