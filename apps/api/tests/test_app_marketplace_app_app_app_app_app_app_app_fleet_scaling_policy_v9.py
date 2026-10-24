from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_scaling_policy_v9 import fleet_scaling_policy_v9
def test_sp3_v9():
    r = fleet_scaling_policy_v9([{"active": True, "scale_ups_today": 5, "scale_downs_today": 3}])
    assert r["scale_ups_today"] == 5
    assert r["healthy"]
