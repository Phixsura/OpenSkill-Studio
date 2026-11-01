from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_zeppelin import fleet_zeppelin_status
def test_zp():
    r = fleet_zeppelin_status([{"running": True, "notebooks": 200, "interpreters": 10}])
    assert r["notebooks"] == 200
    assert r["all_running"]
