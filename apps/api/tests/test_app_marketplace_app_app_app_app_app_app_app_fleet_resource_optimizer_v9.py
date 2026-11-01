from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_resource_optimizer_v9 import fleet_resource_optimizer_v9
def test_ro_v9():
    r = fleet_resource_optimizer_v9([{"applied": True, "savings_monthly": 2000, "cpu_cores_saved": 10}])
    assert r["savings_monthly"] == 2000
    assert r["healthy"]
