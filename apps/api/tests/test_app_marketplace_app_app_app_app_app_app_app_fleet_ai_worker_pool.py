from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_worker_pool import fleet_ai_worker_pool
def test_wp():
    r = fleet_ai_worker_pool([{"active": True, "workers": 500, "busy": 400}])
    assert r["utilization"] == 80.0
    assert r["efficient"]
