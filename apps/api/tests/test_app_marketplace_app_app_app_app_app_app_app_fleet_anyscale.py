from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_anyscale import fleet_anyscale_status
def test_as():
    r = fleet_anyscale_status([{"status": "RUNNING", "nodes": 50, "active_jobs": 20}])
    assert r["nodes"] == 50
    assert r["all_running"]
