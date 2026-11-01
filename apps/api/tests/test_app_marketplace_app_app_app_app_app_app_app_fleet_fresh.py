from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_fresh import fleet_fresh_status
def test_fresh():
    r = fleet_fresh_status([{"running": True, "islands": 20, "routes": 40}])
    assert r["islands"] == 20
    assert r["all_running"]
