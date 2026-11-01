from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ecs import fleet_ecs_status
def test_ecs():
    r = fleet_ecs_status([{"status": "ACTIVE", "running_count": 10, "desired_count": 10}])
    assert r["stable"]
    assert r["running_tasks"] == 10
