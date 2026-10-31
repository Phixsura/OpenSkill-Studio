from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_fargate import fleet_fargate_status
def test_fg():
    r = fleet_fargate_status([{"status": "RUNNING", "cpu": 256, "memory_mb": 512}])
    assert r["cpu_units"] == 256
    assert r["all_running"]
