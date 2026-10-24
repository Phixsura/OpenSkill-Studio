from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_alloc import fleet_ai_cost_allocation
def test_ca():
    r = fleet_ai_cost_allocation([{"active": True, "teams": 20, "total_usd": 500000, "allocated_pct": 98}])
    assert r["total_usd"] == 500000
    assert r["tracked"]
