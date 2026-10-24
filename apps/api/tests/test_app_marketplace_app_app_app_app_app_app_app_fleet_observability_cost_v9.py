from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_observability_cost_v9 import fleet_observability_cost_v9
def test_oc_v9():
    r = fleet_observability_cost_v9([{"monthly_cost": 5000, "metrics_cost": 2000, "logs_cost": 2000, "traces_cost": 1000}])
    assert r["total_monthly"] == 5000
    assert r["healthy"]
