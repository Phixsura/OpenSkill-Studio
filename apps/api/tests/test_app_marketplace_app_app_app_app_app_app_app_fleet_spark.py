from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_spark import fleet_spark_status
def test_spark():
    r = fleet_spark_status([{"state": "RUNNING", "executors": 50, "active_jobs": 10}])
    assert r["executors"] == 50
    assert r["all_running"]
