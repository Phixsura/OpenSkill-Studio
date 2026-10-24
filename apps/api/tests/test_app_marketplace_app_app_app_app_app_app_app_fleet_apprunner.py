from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_apprunner import fleet_apprunner_status
def test_ar():
    r = fleet_apprunner_status([{"status": "RUNNING", "instances": 5, "requests_24h": 1000000}])
    assert r["instances"] == 5
    assert r["all_running"]
