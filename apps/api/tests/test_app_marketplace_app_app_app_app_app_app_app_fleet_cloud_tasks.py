from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_tasks import fleet_cloud_tasks
def test_ct():
    r = fleet_cloud_tasks([{"state": "RUNNING", "dispatched_24h": 1000000, "success_rate": 99.9}])
    assert r["tasks_24h"] == 1000000
    assert r["reliable"]
