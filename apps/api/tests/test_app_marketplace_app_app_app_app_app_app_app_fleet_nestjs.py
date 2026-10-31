from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_nestjs import fleet_nestjs_status
def test_nj():
    r = fleet_nestjs_status([{"running": True, "modules": 50, "endpoints": 200}])
    assert r["modules"] == 50
    assert r["all_running"]
