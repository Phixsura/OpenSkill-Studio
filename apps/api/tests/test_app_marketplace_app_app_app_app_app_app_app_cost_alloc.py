from app.services.app_marketplace_app_app_app_app_app_app_app_cost_alloc import allocate_costs, compare_periods

def test_allocate():
    r = allocate_costs([
        {"team": "platform", "project": "api", "cost": 500.0},
        {"team": "platform", "project": "web", "cost": 300.0},
        {"team": "data", "project": "pipeline", "cost": 200.0},
    ])
    assert r["total_cost"] == 1000.0
    assert r["by_team"]["platform"] == 800.0
    assert r["top_team"] == "platform"
    assert r["project_count"] == 3

def test_compare():
    c = allocate_costs([{"cost": 1200}])
    p = allocate_costs([{"cost": 1000}])
    r = compare_periods(c, p)
    assert r["delta"] == 200.0
    assert r["trend"] == "up"
    assert r["pct_change"] == 20.0
