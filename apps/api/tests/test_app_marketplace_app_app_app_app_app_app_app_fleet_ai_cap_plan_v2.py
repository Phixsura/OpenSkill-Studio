from app.services.app_marketplace_app_app_app_app_app_app_app_fleet_ai_cap_plan_v2 import fleet_ai_capacity_planner_v2
def test_cpv2():
    r = fleet_ai_capacity_planner_v2([{"active": True, "days": 180, "accuracy": 92, "savings_pct": 25}])
    assert r["forecast_days"] == 180
    assert r["predictive"]
