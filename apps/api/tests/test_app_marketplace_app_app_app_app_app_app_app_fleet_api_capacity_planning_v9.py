from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_api_capacity_planning_v9 import fleet_api_capacity_planning_v9
def test_acpl_v9():
    r = fleet_api_capacity_planning_v9([{"growth_pct_monthly": 10, "max_rps": 100000, "utilization_pct": 50}])
    assert r["avg_utilization_pct"] == 50.0
    assert r["healthy"]
