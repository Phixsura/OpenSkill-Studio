from app.services.app_marketplace_app_app_app_app_app_app_app_cost_alloc import allocate_costs, budget_vs_actual

def test_allocate():
    r = allocate_costs([
        {"team": "platform", "service": "api", "monthly_cost": 500},
        {"team": "platform", "service": "db", "monthly_cost": 300},
        {"team": "data", "service": "pipeline", "monthly_cost": 200},
    ])
    assert r["total_cost"] == 1000
    assert r["by_team"][0]["team"] == "platform"
    assert r["by_team"][0]["pct"] == 80.0

def test_budget():
    r = budget_vs_actual(1000, 1150)
    assert r["status"] == "over"
    assert r["variance"] == 150
    r2 = budget_vs_actual(1000, 950)
    assert r2["status"] == "under"
