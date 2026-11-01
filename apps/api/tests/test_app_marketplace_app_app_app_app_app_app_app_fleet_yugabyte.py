from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_yugabyte import fleet_yugabyte_status
def test_yb():
    r = fleet_yugabyte_status([{"status": "RUNNING", "tablets": 3000, "tservers": 9}])
    assert r["tablets"] == 3000
    assert r["all_running"]
