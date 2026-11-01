from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_cost_sum import fleet_cost_summary
def test_summary():
    r = fleet_cost_summary([{"cost": 100}, {"cost": 200}, {"cost": 300}])
    assert r["total_cost"] == 600
    assert r["avg_cost"] == 200
