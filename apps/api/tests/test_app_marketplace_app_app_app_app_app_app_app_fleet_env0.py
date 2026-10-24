from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_env0 import fleet_env0_status
def test_env0():
    r = fleet_env0_status([{"active": True, "monthly_cost_usd": 1000, "ttl_enforced": True}, {"active": True, "monthly_cost_usd": 500, "ttl_enforced": False}])
    assert r["monthly_cost"] == 1500
    assert not r["cost_controlled"]
