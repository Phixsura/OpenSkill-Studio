from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gx import fleet_gx_status
def test_gx():
    r = fleet_gx_status([{"active": True, "expectations": 500, "validations_24h": 10000, "success_rate": 99.5}])
    assert r["expectations"] == 500
    assert r["success_rate"] == 99.5
