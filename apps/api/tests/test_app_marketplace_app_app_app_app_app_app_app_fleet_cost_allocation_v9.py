from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_allocation_v9 import fleet_cost_allocation_v9
def test_ca3_v9():
    r = fleet_cost_allocation_v9([{"tagged": True, "unallocated_pct": 2, "monthly_cost": 50000}])
    assert r["unallocated_pct"] == 2.0
    assert r["healthy"]
