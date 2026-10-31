from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cloud_sched import fleet_cloud_scheduler
def test_cs():
    r = fleet_cloud_scheduler([{"state": "ENABLED", "executions_24h": 500, "failed_24h": 0}])
    assert r["executions_24h"] == 500
    assert r["reliable"]
