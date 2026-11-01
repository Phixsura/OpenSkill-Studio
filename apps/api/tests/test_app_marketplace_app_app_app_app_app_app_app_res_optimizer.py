from app.services.app_marketplace_app_app_app_app_app_app_app_res_optimizer import analyze_waste, optimization_plan

def test_waste():
    r = analyze_waste([
        {"name": "idle-vm", "usage_pct": 2, "monthly_cost": 200},
        {"name": "dev-db", "usage_pct": 25, "monthly_cost": 100},
        {"name": "prod-api", "usage_pct": 75, "monthly_cost": 500},
    ])
    assert r["waste_count"] == 2
    assert r["total_waste_cost"] > 0

def test_plan():
    waste = analyze_waste([
        {"name": "a", "usage_pct": 5, "monthly_cost": 100},
        {"name": "b", "usage_pct": 20, "monthly_cost": 50},
    ])
    p = optimization_plan(waste)
    assert p["immediate_actions"] == 1
    assert p["scheduled_actions"] == 1
