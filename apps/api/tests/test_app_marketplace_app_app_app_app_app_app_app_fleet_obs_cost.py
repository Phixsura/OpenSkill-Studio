from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_obs_cost import fleet_obs_cost
def test_obs_cost():
    r = fleet_obs_cost([{"type": "logs", "monthly_cost": 5000}, {"type": "metrics", "monthly_cost": 3000}, {"type": "traces", "monthly_cost": 4000}])
    assert r["total_monthly"] == 12000
    assert r["expensive"]
