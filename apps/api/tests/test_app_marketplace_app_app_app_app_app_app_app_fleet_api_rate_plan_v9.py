from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_rate_plan_v9 import fleet_api_rate_plan_v9
def test_arp_v9():
    r = fleet_api_rate_plan_v9([{"active": True, "subscribers": 500, "monthly_quota": 1000000}])
    assert r["subscribers"] == 500
    assert r["healthy"]
