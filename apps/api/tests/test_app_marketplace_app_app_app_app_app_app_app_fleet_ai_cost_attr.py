from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cost_attr import fleet_ai_cost_attribution
def test_ca():
    r = fleet_ai_cost_attribution([{"name": "ML Team", "monthly_cost": 50000}, {"name": "Platform", "monthly_cost": 30000}])
    assert r["total_monthly"] == 80000
    assert r["top_spender"] == "ML Team"
