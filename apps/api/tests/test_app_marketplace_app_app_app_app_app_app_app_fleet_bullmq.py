from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_bullmq import fleet_bullmq_status
def test_bm():
    r = fleet_bullmq_status([{"waiting": 50, "active": 10, "completed_24h": 5000, "failed_24h": 0}])
    assert r["completed_24h"] == 5000
    assert r["healthy"]
