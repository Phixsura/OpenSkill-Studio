from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_comet import fleet_comet_status
def test_comet():
    r = fleet_comet_status([{"active": True, "experiments": 5000, "panels": 200}])
    assert r["experiments"] == 5000
    assert r["all_active"]
