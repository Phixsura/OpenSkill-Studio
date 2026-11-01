from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_load_shedding_v9 import fleet_api_load_shedding_v9
def test_als_v9():
    r = fleet_api_load_shedding_v9([{"shedding_active": False, "shed_today": 0, "total_today": 100000}])
    assert r["shedding_active"] == 0
    assert r["healthy"]
