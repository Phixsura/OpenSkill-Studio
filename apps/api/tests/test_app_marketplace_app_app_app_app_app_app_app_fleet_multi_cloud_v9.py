from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_multi_cloud_v9 import fleet_multi_cloud_v9
def test_mc_v9():
    r = fleet_multi_cloud_v9([{"active": True, "instances": 200, "monthly_spend": 50000}, {"active": True, "instances": 150, "monthly_spend": 30000}])
    assert r["total_instances"] == 350
    assert r["healthy"]
