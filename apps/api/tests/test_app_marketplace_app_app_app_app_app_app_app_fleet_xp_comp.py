from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_xp_comp import fleet_xp_compositions
def test_xp():
    r = fleet_xp_compositions([{"ready": True, "managed_resources": 50}, {"ready": False, "managed_resources": 30}])
    assert r["managed_resources"] == 80
    assert not r["all_ready"]
