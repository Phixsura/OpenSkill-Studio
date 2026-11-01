from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_gofiber import fleet_gofiber_status
def test_gf():
    r = fleet_gofiber_status([{"running": True, "rps": 200000, "goroutines": 5000}])
    assert r["rps"] == 200000
    assert r["all_running"]
