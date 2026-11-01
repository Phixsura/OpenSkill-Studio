from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_spec_v9 import fleet_api_spec_v9
def test_aspec_v9():
    r = fleet_api_spec_v9([{"valid": True, "auto_generated": True, "versions": 5}])
    assert r["valid"] == 1
    assert r["healthy"]
