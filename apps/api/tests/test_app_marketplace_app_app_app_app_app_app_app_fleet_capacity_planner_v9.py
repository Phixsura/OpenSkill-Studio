from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_capacity_planner_v9 import fleet_capacity_planner_v9
def test_cap_v9():
    r = fleet_capacity_planner_v9([{"used": 60, "capacity": 100}, {"used": 50, "capacity": 100}])
    assert r["utilization_pct"] == 55.0
    assert r["healthy"]
    assert not r["needs_scaling"]
