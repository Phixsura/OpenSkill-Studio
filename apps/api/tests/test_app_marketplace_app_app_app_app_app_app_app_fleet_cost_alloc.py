from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_alloc import fleet_cost_allocation
def test_alloc():
    r = fleet_cost_allocation([{"team": "platform", "cost": 600}, {"team": "product", "cost": 400}])
    assert r["total_cost"] == 1000
    assert r["allocation"]["platform"] == 60.0
    assert r["top_spender"] == "platform"
