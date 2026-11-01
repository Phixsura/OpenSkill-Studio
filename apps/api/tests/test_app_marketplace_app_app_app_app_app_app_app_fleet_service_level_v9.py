from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_service_level_v9 import fleet_service_level_v9
def test_sl_v9():
    r = fleet_service_level_v9([{"met": True, "at_risk": False, "breached": False}])
    assert r["met"] == 1
    assert r["breached"] == 0
    assert r["healthy"]
