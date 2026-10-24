from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resource_lock_v9 import fleet_resource_lock_v9
def test_rl2_v9():
    r = fleet_resource_lock_v9([{"held": True, "expired": False, "contentions": 2}])
    assert r["held"] == 1
    assert r["healthy"]
